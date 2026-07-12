"""
ModuleRepository

Two public methods, one internal tree-builder.

  get_root_modules()  — returns all root modules as trees
  get_module(id)      — returns one module as a tree

Tree-building strategy
----------------------
1. Collect all node IDs with a simple recursive CTE (no aggregates in the
   recursive term, which PostgreSQL forbids).
2. Enrich every ID in one query against module_card_view (counts are
   already computed there).
3. Fetch skills and links for all nodes in two bulk queries.
4. Assemble nesting in Python.

OG metadata
-----------
On every read, any link row with og_title IS NULL is refreshed in-place:
the links table is updated and the fresh values are used in the response.
"""

from sqlalchemy import text
from sqlalchemy.orm import Session

from app.services.link_services import LinkService


class ModuleRepository:
    def __init__(self, db: Session):
        self.db = db

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def get_root_modules(self) -> list[dict]:
        root_rows = self.db.execute(
            text("""
                SELECT id
                FROM modules
                WHERE parent_id IS NULL
                ORDER BY order_index ASC
            """)
        ).mappings().all()

        results = []
        for row in root_rows:
            tree = self._build_tree(row["id"])
            if tree is not None:
                results.append(tree)
        return results

    def get_module(self, module_id: int) -> dict | None:
        """
        Returns a single module with its full descendant tree.
        Returns None if module_id does not exist.
        """
        return self._build_tree(module_id)

    def exists(self, module_id: int) -> bool:
        """Lightweight check — does this module exist?"""
        row = self.db.execute(
            text("SELECT 1 FROM modules WHERE id = :id"),
            {"id": module_id},
        ).first()
        return row is not None

    # ------------------------------------------------------------------
    # Internal tree builder
    # ------------------------------------------------------------------

    def _build_tree(self, root_id: int) -> dict | None:
        # ---- Step 1: collect all node IDs via recursive CTE -----------
        id_rows = self.db.execute(
            text("""
                WITH RECURSIVE subtree AS (
                    SELECT id, parent_id, order_index
                    FROM modules
                    WHERE id = :root_id

                    UNION ALL

                    SELECT m.id, m.parent_id, m.order_index
                    FROM modules m
                    JOIN subtree s ON m.parent_id = s.id
                )
                SELECT id FROM subtree
            """),
            {"root_id": root_id},
        ).mappings().all()

        if not id_rows:
            return None

        ids = [r["id"] for r in id_rows]

        # ---- Step 2: enrich from module_card_view ---------------------
        card_rows = self.db.execute(
            text("""
                SELECT *
                FROM module_card_view
                WHERE id = ANY(:ids)
            """),
            {"ids": ids},
        ).mappings().all()

        nodes: dict[int, dict] = {}
        for row in card_rows:
            node = dict(row)
            node["skills"] = []
            node["links"] = []
            node["children"] = []
            nodes[node["id"]] = node

        # ---- Step 3: bulk-fetch skills --------------------------------
        skill_rows = self.db.execute(
            text("""
                SELECT ms.module_id, s.id, s.name, s.slug
                FROM skills s
                JOIN module_skills ms ON ms.skill_id = s.id
                WHERE ms.module_id = ANY(:ids)
                ORDER BY s.name ASC
            """),
            {"ids": ids},
        ).mappings().all()

        for row in skill_rows:
            mid = row["module_id"]
            if mid in nodes:
                nodes[mid]["skills"].append({
                    "id": row["id"],
                    "name": row["name"],
                    "slug": row["slug"],
                })

        # ---- Step 4: bulk-fetch links ---------------------------------
        link_rows = self.db.execute(
            text("""
                SELECT ml.module_id,
                       ml.id AS module_link_id,
                       l.id, l.title, l.url, l.description, l.link_type,
                       ml.sub_link_type,
                       l.og_title, l.og_description, l.og_image,
                       ml.order_index
                FROM links l
                JOIN module_links ml ON ml.link_id = l.id
                WHERE ml.module_id = ANY(:ids)
                ORDER BY ml.module_id ASC, ml.order_index ASC
            """),
            {"ids": ids},
        ).mappings().all()

        # ---- Step 4a: backfill missing OG metadata // the backfill is takeing too long so that was removed --------------------
        enriched_links = [(dict(row)) for row in link_rows]

        for row in enriched_links:
            mid = row["module_id"]
            if mid in nodes:
                nodes[mid]["links"].append({
                    "module_link_id": row["module_link_id"],
                    "id":             row["id"],
                    "title":          row["title"],
                    "url":            row["url"],
                    "description":    row["description"],
                    "link_type":      row["link_type"],
                    "sub_link_type":  row["sub_link_type"],
                    "og_title":       row["og_title"],
                    "og_description": row["og_description"],
                    "og_image":       row["og_image"],
                    "order_index":    row["order_index"],
                })

        # ---- Step 5: assemble nested tree in Python -------------------
        root = None
        for node in nodes.values():
            pid = node.get("parent_id")
            if pid is None or pid not in nodes:
                root = node
            else:
                nodes[pid]["children"].append(node)

        for node in nodes.values():
            node["children"].sort(key=lambda c: c.get("order_index", 0))

        return root

        """
        If og_title is missing, fetch OG metadata, persist it to the
        links table, and return the row with updated values.
        Skips the network call if og_title is already populated.
        """
        if row.get("og_title"):
            return row

        metadata = LinkService.fetch_metadata(row["url"])

        self.db.execute(
            text("""
                UPDATE links
                SET
                    og_title       = :og_title,
                    og_description = :og_description,
                    og_image       = :og_image,
                    og_fetched_at  = :og_fetched_at
                WHERE id = :id
            """),
            {
                "id":             row["id"],
                "og_title":       metadata["og_title"],
                "og_description": metadata["og_description"],
                "og_image":       metadata["og_image"],
                "og_fetched_at":  metadata["fetched_at"],
            },
        )
        self.db.flush()

        row["og_title"]       = metadata["og_title"]
        row["og_description"] = metadata["og_description"]
        row["og_image"]       = metadata["og_image"]

        return row