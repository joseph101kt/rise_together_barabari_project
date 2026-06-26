"""
ModuleRepository

Touches:
  - module_card_view  (SQL view created at startup)
  - modules           (for tree recursion via CTE)
  - module_links + links
  - module_skills + skills
"""

from typing import Any

from sqlalchemy import text
from sqlalchemy.orm import Session


class ModuleRepository:
    def __init__(self, db: Session):
        self.db = db

    # ------------------------------------------------------------------
    # module_card_view  — flat card list
    # ------------------------------------------------------------------

    def get_card_list(self, parent_id: int | None = None) -> list[dict]:
        """
        Returns a list of module cards.
        Defaults to root-level (parent_id IS NULL).
        Pass a parent_id to get direct children.
        """
        if parent_id is None:
            rows = self.db.execute(
                text("""
                    SELECT *
                    FROM module_card_view
                    WHERE parent_id IS NULL
                    ORDER BY order_index ASC
                """)
            ).mappings().all()
        else:
            rows = self.db.execute(
                text("""
                    SELECT *
                    FROM module_card_view
                    WHERE parent_id = :parent_id
                    ORDER BY order_index ASC
                """),
                {"parent_id": parent_id},
            ).mappings().all()

        return [dict(row) for row in rows]

    # ------------------------------------------------------------------
    # module_details_view  — card + skills + links + direct children
    # ------------------------------------------------------------------

    def get_details(self, module_id: int) -> dict | None:
        """
        Returns a single module with its skills, links, and direct children.
        Returns None if not found.
        """
        # 1. The module card itself
        row = self.db.execute(
            text("SELECT * FROM module_card_view WHERE id = :id"),
            {"id": module_id},
        ).mappings().first()

        if not row:
            return None

        module = dict(row)

        # 2. Skills attached to this module
        skill_rows = self.db.execute(
            text("""
                SELECT s.id, s.name, s.slug
                FROM skills s
                JOIN module_skills ms ON ms.skill_id = s.id
                WHERE ms.module_id = :module_id
                ORDER BY s.name ASC
            """),
            {"module_id": module_id},
        ).mappings().all()

        # 3. Links attached to this module, ordered by order_index
        link_rows = self.db.execute(
            text("""
                SELECT l.id, l.title, l.url, l.description, l.link_type,
                       l.og_title, l.og_description, l.og_image,
                       ml.order_index
                FROM links l
                JOIN module_links ml ON ml.link_id = l.id
                WHERE ml.module_id = :module_id
                ORDER BY ml.order_index ASC
            """),
            {"module_id": module_id},
        ).mappings().all()

        # 4. Direct children (uses the view so counts are included)
        children = self.get_card_list(parent_id=module_id)

        return {
            "module": module,
            "skills": [dict(r) for r in skill_rows],
            "links": [dict(r) for r in link_rows],
            "children": children,
        }

    # ------------------------------------------------------------------
    # module_tree — recursive CTE, max 4 levels deep
    # ------------------------------------------------------------------

    def get_tree(self, module_id: int) -> dict | None:
        """
        Returns a module and all its descendants as a nested tree.
        Uses a recursive CTE so it's a single query.
        Assembles nesting in Python.
        """
        rows = self.db.execute(
            text("""
                WITH RECURSIVE module_tree AS (
                    -- anchor: the requested root
                    SELECT
                        m.id, m.parent_id, m.module_type, m.title,
                        m.description, m.estimated_completion_time,
                        m.created_by, m.order_index, m.created_at, m.updated_at,
                        COUNT(DISTINCT ml.link_id)     AS resource_count,
                        COUNT(DISTINCT ms.skill_id)    AS skill_count,
                        COUNT(DISTINCT mstar.user_id)  AS star_count,
                        0 AS depth
                    FROM modules m
                    LEFT JOIN module_links  ml    ON ml.module_id    = m.id
                    LEFT JOIN module_skills ms    ON ms.module_id    = m.id
                    LEFT JOIN module_stars  mstar ON mstar.module_id = m.id
                    WHERE m.id = :module_id
                    GROUP BY m.id

                    UNION ALL

                    -- recursive: children of each row already in the CTE
                    SELECT
                        m.id, m.parent_id, m.module_type, m.title,
                        m.description, m.estimated_completion_time,
                        m.created_by, m.order_index, m.created_at, m.updated_at,
                        COUNT(DISTINCT ml.link_id)     AS resource_count,
                        COUNT(DISTINCT ms.skill_id)    AS skill_count,
                        COUNT(DISTINCT mstar.user_id)  AS star_count,
                        mt.depth + 1
                    FROM modules m
                    JOIN module_tree mt ON m.parent_id = mt.id
                    LEFT JOIN module_links  ml    ON ml.module_id    = m.id
                    LEFT JOIN module_skills ms    ON ms.module_id    = m.id
                    LEFT JOIN module_stars  mstar ON mstar.module_id = m.id
                    WHERE mt.depth < 4   -- max depth guard
                    GROUP BY m.id, mt.depth
                )
                SELECT * FROM module_tree
                ORDER BY depth ASC, order_index ASC
            """),
            {"module_id": module_id},
        ).mappings().all()

        if not rows:
            return None

        # Assemble flat rows into nested tree
        nodes: dict[int, dict] = {}
        for row in rows:
            node = dict(row)
            node["children"] = []
            nodes[node["id"]] = node

        root = None
        for node in nodes.values():
            pid = node.get("parent_id")
            if pid is None or pid not in nodes:
                root = node
            else:
                nodes[pid]["children"].append(node)

        return root