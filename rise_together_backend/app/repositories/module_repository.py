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

"""

from sqlalchemy import text
from sqlalchemy.orm import Session
import time



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
        import time

        overall_start = time.perf_counter()

        # ------------------------------------------------------------------
        # Step 1: Collect all module IDs in the subtree
        # ------------------------------------------------------------------
        t = time.perf_counter()

        id_rows = self.db.execute(
            text("""
                WITH RECURSIVE subtree AS (
                    SELECT id, parent_id, order_index
                    FROM modules
                    WHERE id = :root_id

                    UNION ALL

                    SELECT m.id, m.parent_id, m.order_index
                    FROM modules m
                    JOIN subtree s
                        ON m.parent_id = s.id
                )
                SELECT id
                FROM subtree
            """),
            {"root_id": root_id},
        ).mappings().all()

        print(f"[ModuleRepository] Step 1 (recursive ids): {time.perf_counter() - t:.3f}s")

        if not id_rows:
            return None

        ids = [row["id"] for row in id_rows]

        # ------------------------------------------------------------------
        # Step 2: Fetch module cards
        # ------------------------------------------------------------------
        t = time.perf_counter()

        card_rows = self.db.execute(
            text("""
                SELECT *
                FROM module_card_view
                WHERE id = ANY(:ids)
            """),
            {"ids": ids},
        ).mappings().all()

        print(f"[ModuleRepository] Step 2 (module_card_view): {time.perf_counter() - t:.3f}s")

        nodes: dict[int, dict] = {}

        for row in card_rows:
            node = dict(row)
            node["skills"] = []
            node["links"] = []
            node["children"] = []
            nodes[node["id"]] = node

        # ------------------------------------------------------------------
        # Step 3: Fetch skills
        # ------------------------------------------------------------------
        t = time.perf_counter()

        skill_rows = self.db.execute(
            text("""
                SELECT
                    ms.module_id,
                    s.id,
                    s.name,
                    s.slug
                FROM module_skills ms
                JOIN skills s
                    ON s.id = ms.skill_id
                WHERE ms.module_id = ANY(:ids)
                ORDER BY ms.module_id, s.name
            """),
            {"ids": ids},
        ).mappings().all()

        print(f"[ModuleRepository] Step 3 (skills): {time.perf_counter() - t:.3f}s")

        for row in skill_rows:
            nodes[row["module_id"]]["skills"].append({
                "id": row["id"],
                "name": row["name"],
                "slug": row["slug"],
            })

        # ------------------------------------------------------------------
        # Step 4: Fetch links
        # ------------------------------------------------------------------
        t = time.perf_counter()

        link_rows = self.db.execute(
            text("""
                SELECT
                    ml.module_id,
                    ml.id AS module_link_id,
                    l.id,
                    l.title,
                    l.url,
                    l.description,
                    l.link_type,
                    ml.sub_link_type,
                    l.og_title,
                    l.og_description,
                    l.og_image,
                    ml.order_index
                FROM module_links ml
                JOIN links l
                    ON l.id = ml.link_id
                WHERE ml.module_id = ANY(:ids)
                ORDER BY ml.module_id, ml.order_index
            """),
            {"ids": ids},
        ).mappings().all()

        print(f"[ModuleRepository] Step 4 (links): {time.perf_counter() - t:.3f}s")

        for row in link_rows:
            nodes[row["module_id"]]["links"].append({
                "module_link_id": row["module_link_id"],
                "id": row["id"],
                "title": row["title"],
                "url": row["url"],
                "description": row["description"],
                "link_type": row["link_type"],
                "sub_link_type": row["sub_link_type"],
                "og_title": row["og_title"],
                "og_description": row["og_description"],
                "og_image": row["og_image"],
                "order_index": row["order_index"],
            })

        # ------------------------------------------------------------------
        # Step 5: Build tree
        # ------------------------------------------------------------------
        t = time.perf_counter()

        root = None

        for node in nodes.values():
            parent_id = node["parent_id"]

            if parent_id is None or parent_id not in nodes:
                root = node
            else:
                nodes[parent_id]["children"].append(node)

        for node in nodes.values():
            node["children"].sort(key=lambda child: child["order_index"])

        print(f"[ModuleRepository] Step 5 (tree build): {time.perf_counter() - t:.3f}s")
        print(f"[ModuleRepository] Total: {time.perf_counter() - overall_start:.3f}s")

        return root   

    # ------------------------------------------------------------------
    # NEW — Top-level root modules ONLY, no children fetched at all
    # ------------------------------------------------------------------
    def get_all_root_modules_only(self) -> list[dict]:
        """
        Standalone method. Returns ONLY modules where parent_id IS NULL.
        Does not fetch or nest any children — children is always [].
        Fully independent — does not call _build_tree or any other method.
        """
        card_rows = self.db.execute(
            text("""
                SELECT *
                FROM module_card_view
                WHERE parent_id IS NULL
                ORDER BY order_index ASC
            """)
        ).mappings().all()

        if not card_rows:
            return []

        root_ids = [row["id"] for row in card_rows]
        results = []
        nodes: dict[int, dict] = {}

        for row in card_rows:
            node = dict(row)
            node["skills"] = []
            node["links"] = []
            node["children"] = []  # always empty — no descendants fetched
            nodes[node["id"]] = node
            results.append(node)

        # Skills/links only for the root rows themselves (not children)
        skill_rows = self.db.execute(
            text("""
                SELECT ms.module_id, s.id, s.name, s.slug
                FROM module_skills ms
                JOIN skills s ON s.id = ms.skill_id
                WHERE ms.module_id = ANY(:ids)
                ORDER BY ms.module_id, s.name
            """),
            {"ids": root_ids},
        ).mappings().all()

        for row in skill_rows:
            m_id = row["module_id"]
            if m_id in nodes:
                nodes[m_id]["skills"].append({
                    "id": row["id"], "name": row["name"], "slug": row["slug"]
                })

        link_rows = self.db.execute(
            text("""
                SELECT ml.module_id, ml.id AS module_link_id, l.id, l.title, l.url,
                       l.description, l.link_type, ml.sub_link_type, l.og_title,
                       l.og_description, l.og_image, ml.order_index
                FROM module_links ml
                JOIN links l ON l.id = ml.link_id
                WHERE ml.module_id = ANY(:ids)
                ORDER BY ml.module_id, ml.order_index
            """),
            {"ids": root_ids},
        ).mappings().all()

        for row in link_rows:
            m_id = row["module_id"]
            if m_id in nodes:
                nodes[m_id]["links"].append({
                    "module_link_id": row["module_link_id"], "id": row["id"],
                    "title": row["title"], "url": row["url"], "description": row["description"],
                    "link_type": row["link_type"], "sub_link_type": row["sub_link_type"],
                    "og_title": row["og_title"], "og_description": row["og_description"],
                    "og_image": row["og_image"], "order_index": row["order_index"]
                })

        return results