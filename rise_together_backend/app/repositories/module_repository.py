from sqlalchemy import text
from sqlalchemy.orm import Session
import time

class ModuleRepository:
    def __init__(self, db: Session):
        self.db = db

    # ------------------------------------------------------------------
    # 1. GET ONLY ROOT MODULES (Nested Tree Forest)
    # ------------------------------------------------------------------
    def get_root_modules(self) -> list[dict]:
        """Returns ONLY modules where parent_id IS NULL, with fully nested child trees."""
        overall_start = time.perf_counter()

        # Step 1: Fetch absolutely every module card row to build the global tree frame
        card_rows = self.db.execute(
            text("SELECT * FROM module_card_view WHERE parent_id IS NULL ORDER BY order_index ASC")
        ).mappings().all()

        if not card_rows:
            return []

        # Step 2: Initialize nodes index map
        nodes: dict[int, dict] = {}
        all_ids = []
        for row in card_rows:
            node = dict(row)
            node["skills"] = []
            node["links"] = []
            node["children"] = []
            nodes[node["id"]] = node
            all_ids.append(node["id"])

        # Step 3: Fetch all relational items in bulk
        self._populate_skills_and_links(nodes, all_ids)

        # Step 4: Build tree topology safely
        root_modules = []
        for node in nodes.values():
            parent_id = node["parent_id"]
            if parent_id is None:
                root_modules.append(node)
            elif parent_id in nodes:
                nodes[parent_id]["children"].append(node)

        # Step 5: Sort child arrays explicitly by order index
        for node in nodes.values():
            node["children"].sort(key=lambda child: child["order_index"])

        # Sort top-level roots
        root_modules.sort(key=lambda root: root["order_index"])

        print(f"[ModuleRepository] get_root_modules total: {time.perf_counter() - overall_start:.3f}s")
        return root_modules


    # ------------------------------------------------------------------
    # 2. GET ALL MODULES (Flat Array Dump)
    # ------------------------------------------------------------------
    def get_all_modules(self) -> list[dict]:
        """Returns ALL modules in the database as a single flat list with empty child arrays."""
        overall_start = time.perf_counter()

        card_rows = self.db.execute(
            text("SELECT * FROM module_card_view ORDER BY order_index ASC")
        ).mappings().all()

        if not card_rows:
            return []

        nodes: dict[int, dict] = {}
        all_ids = []
        flat_results = []

        for row in card_rows:
            node = dict(row)
            node["skills"] = []
            node["links"] = []
            node["children"] = [] # Kept empty to represent a clean flat schema layout
            nodes[node["id"]] = node
            all_ids.append(node["id"])
            flat_results.append(node)

        # Bulk fetch skills and links
        self._populate_skills_and_links(nodes, all_ids)

        print(f"[ModuleRepository] get_all_modules total: {time.perf_counter() - overall_start:.3f}s")
        return flat_results


    # ------------------------------------------------------------------
    # 3. GET SINGLE MODULE (Targeted Subtree)
    # ------------------------------------------------------------------
    def get_module(self, module_id: int) -> dict | None:
        """Returns a single specific module and its complete downstream child tree."""
        # Reuse root structural parsing logic but filter down to the target node
        all_roots = self.get_root_modules()
        
        # Helper function to find a specific ID inside a tree forest
        def find_node(tree_list: list[dict], target_id: int) -> dict | None:
            for node in tree_list:
                if node["id"] == target_id:
                    return node
                found = find_node(node["children"], target_id)
                if found:
                    return found
            return None

        return find_node(all_roots, module_id)


    # ------------------------------------------------------------------
    # Private Core Shared Helper
    # ------------------------------------------------------------------
    def _populate_skills_and_links(self, nodes: dict[int, dict], ids: list[int]) -> None:
        """Helper tool to stitch skills and links records into active node structures in-place."""
        if not ids:
            return

        # Fetch Skills
        skill_rows = self.db.execute(
            text("""
                SELECT ms.module_id, s.id, s.name, s.slug
                FROM module_skills ms
                JOIN skills s ON s.id = ms.skill_id
                WHERE ms.module_id = ANY(:ids)
                ORDER BY ms.module_id, s.name
            """),
            {"ids": ids},
        ).mappings().all()

        for row in skill_rows:
            m_id = row["module_id"]
            if m_id in nodes:
                nodes[m_id]["skills"].append({
                    "id": row["id"], "name": row["name"], "slug": row["slug"]
                })

        # Fetch Links
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
            {"ids": ids},
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