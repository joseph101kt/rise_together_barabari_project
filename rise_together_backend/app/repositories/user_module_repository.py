"""
UserModuleRepository

Handles all reads and writes for user_modules and user_module_links.

Public methods
--------------
  get_user_modules(user_id)
      Returns every user_module for the user, each with its submitted links.

  get_user_module(user_id, module_id)
      Returns one user_module with its submitted links, or None.

  create_user_module(user_id, module_id)
      Inserts a user_modules row (status=in_progress).
      Raises if already exists.

  create_user_module_link(user_id, module_id, module_link_id, url, title)
      Inserts into links (link_type=submission) then user_module_links.
      After inserting, syncs the parent user_module status.
      Raises if module_link_id does not belong to module_id.
      Raises if user already has a submission for that slot.

  patch_user_module_link(user_id, module_id, module_link_id, completed)
      Updates completed / completed_at on an existing user_module_link.
      After updating, syncs the parent user_module status.

Status-sync logic
-----------------
After any write to user_module_links:
  - Count all module_link slots for the module.
  - Count how many the user has with completed=true.
  - If all slots are covered and completed → status='completed'.
  - Otherwise → status='in_progress'.
"""

from sqlalchemy import text
from sqlalchemy.orm import Session


class UserModuleRepository:
    def __init__(self, db: Session):
        self.db = db

    # ------------------------------------------------------------------
    # Reads
    # ------------------------------------------------------------------

    def get_user_modules(self, user_id: int) -> list[dict]:
        """All user_modules for this user, each with submitted links."""
        um_rows = self.db.execute(
            text("""
                SELECT
                    user_id,
                    module_id,
                    status,
                    started_at,
                    completed_at
                FROM user_modules
                WHERE user_id = :user_id
                ORDER BY module_id ASC
            """),
            {"user_id": user_id},
        ).mappings().all()

        if not um_rows:
            return []

        module_ids = [r["module_id"] for r in um_rows]

        link_rows = self._fetch_submitted_links(user_id, module_ids)

        # Group links by module_id
        links_by_module: dict[int, list[dict]] = {}
        for row in link_rows:
            mid = row["module_id"]
            links_by_module.setdefault(mid, []).append(dict(row))

        result = []
        for row in um_rows:
            entry = dict(row)
            entry["submitted_links"] = links_by_module.get(row["module_id"], [])
            result.append(entry)

        return result

    def get_user_module(self, user_id: int, module_id: int) -> dict | None:
        """One user_module with submitted links, or None."""
        um_row = self.db.execute(
            text("""
                SELECT
                    user_id,
                    module_id,
                    status,
                    started_at,
                    completed_at
                FROM user_modules
                WHERE user_id = :user_id AND module_id = :module_id
            """),
            {"user_id": user_id, "module_id": module_id},
        ).mappings().first()

        if um_row is None:
            return None

        link_rows = self._fetch_submitted_links(user_id, [module_id])

        entry = dict(um_row)
        entry["submitted_links"] = [dict(r) for r in link_rows]
        return entry

    # ------------------------------------------------------------------
    # Writes
    # ------------------------------------------------------------------

    def create_user_module(self, user_id: int, module_id: int) -> dict:
        """
        Start tracking a module for a user (status=in_progress).
        Raises ValueError if the user_module already exists.
        """
        existing = self.db.execute(
            text("""
                SELECT 1 FROM user_modules
                WHERE user_id = :user_id AND module_id = :module_id
            """),
            {"user_id": user_id, "module_id": module_id},
        ).first()

        if existing:
            raise ValueError(
                f"User {user_id} is already tracking module {module_id}."
            )

        self.db.execute(
            text("""
                INSERT INTO user_modules (user_id, module_id, status, started_at)
                VALUES (
                    :user_id,
                    :module_id,
                    CAST('in_progress' AS user_module_status),
                    now()
                )
            """),
            {"user_id": user_id, "module_id": module_id},
        )
        self.db.commit()

        return self.get_user_module(user_id, module_id)

    def create_user_module_link(
        self,
        user_id: int,
        module_id: int,
        module_link_id: int,
        url: str,
        title: str,
    ) -> dict:
        """
        Submit a link for a specific module-link slot.

        Steps:
        1. Verify module_link_id belongs to module_id.
        2. Verify user does not already have a submission for this slot.
        3. Insert into links (link_type=submission).
        4. Insert into user_module_links.
        5. Sync user_module status.
        6. Return the updated user_module.
        """
        # 1. Verify the slot belongs to this module
        slot = self.db.execute(
            text("""
                SELECT id FROM module_links
                WHERE id = :module_link_id AND module_id = :module_id
            """),
            {"module_link_id": module_link_id, "module_id": module_id},
        ).first()

        if slot is None:
            raise ValueError(
                f"module_link {module_link_id} does not belong to module {module_id}."
            )

        # 2. Verify no existing submission for this slot
        existing = self.db.execute(
            text("""
                SELECT 1 FROM user_module_links
                WHERE user_id = :user_id AND module_link_id = :module_link_id
            """),
            {"user_id": user_id, "module_link_id": module_link_id},
        ).first()

        if existing:
            raise ValueError(
                f"User {user_id} already has a submission for slot {module_link_id}."
            )

        # 3. Insert into links
        link_row = self.db.execute(
            text("""
                INSERT INTO links (title, url, link_type, created_by)
                VALUES (
                    :title,
                    :url,
                    CAST('submission' AS link_type),
                    :created_by
                )
                RETURNING id
            """),
            {"title": title, "url": url, "created_by": user_id},
        ).mappings().first()

        link_id = link_row["id"]

        # 4. Insert into user_module_links
        self.db.execute(
            text("""
                INSERT INTO user_module_links (user_id, module_link_id, link_id, completed)
                VALUES (:user_id, :module_link_id, :link_id, false)
            """),
            {
                "user_id": user_id,
                "module_link_id": module_link_id,
                "link_id": link_id,
            },
        )

        # 5. Sync status
        self._sync_module_status(user_id, module_id)

        self.db.commit()

        return self.get_user_module(user_id, module_id)

    def patch_user_module_link(
        self,
        user_id: int,
        module_id: int,
        module_link_id: int,
        completed: bool,
    ) -> dict:
        """
        Toggle completed on an existing user_module_link.
        Syncs the parent user_module status afterward.
        Raises ValueError if the row does not exist.
        """
        # Verify the row exists
        existing = self.db.execute(
            text("""
                SELECT 1 FROM user_module_links
                WHERE user_id = :user_id AND module_link_id = :module_link_id
            """),
            {"user_id": user_id, "module_link_id": module_link_id},
        ).first()

        if not existing:
            raise ValueError(
                f"No submission found for user {user_id}, slot {module_link_id}."
            )

        self.db.execute(
            text("""
                UPDATE user_module_links
                SET
                    completed    = :completed,
                    completed_at = CASE WHEN :completed THEN now() ELSE NULL END
                WHERE user_id = :user_id AND module_link_id = :module_link_id
            """),
            {
                "user_id": user_id,
                "module_link_id": module_link_id,
                "completed": completed,
            },
        )

        self._sync_module_status(user_id, module_id)
        self.db.commit()

        return self.get_user_module(user_id, module_id)

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _fetch_submitted_links(
        self, user_id: int, module_ids: list[int]
    ) -> list:
        """
        Bulk-fetch all user_module_link rows for the given modules,
        joined to module_links (for order_index) and links (for url/title/type).
        Returns rows ordered by module_id, then slot order_index.
        """
        return self.db.execute(
            text("""
                SELECT
                    ml.module_id,
                    uml.module_link_id,
                    ml.order_index,
                    uml.link_id,
                    l.title       AS link_title,
                    l.url         AS link_url,
                    l.link_type,
                    uml.completed,
                    uml.completed_at
                FROM user_module_links uml
                JOIN module_links ml ON ml.id   = uml.module_link_id
                JOIN links        l  ON l.id    = uml.link_id
                WHERE uml.user_id    = :user_id
                  AND ml.module_id   = ANY(:module_ids)
                ORDER BY ml.module_id ASC, ml.order_index ASC
            """),
            {"user_id": user_id, "module_ids": module_ids},
        ).mappings().all()

    def _sync_module_status(self, user_id: int, module_id: int) -> None:
        """
        Recompute and write user_module.status based on link completion.

        Logic:
          - total  = number of module_link slots for this module
          - done   = number the user has submitted AND marked completed
          - If total > 0 and done >= total → 'completed'
          - Otherwise                      → 'in_progress'

        Called inside an open transaction; caller is responsible for commit.
        """
        counts = self.db.execute(
            text("""
                SELECT
                    COUNT(ml.id)                                           AS total,
                    COUNT(uml.module_link_id)
                        FILTER (WHERE uml.completed = true)                AS done
                FROM module_links ml
                LEFT JOIN user_module_links uml
                       ON uml.module_link_id = ml.id
                      AND uml.user_id        = :user_id
                WHERE ml.module_id = :module_id
            """),
            {"user_id": user_id, "module_id": module_id},
        ).mappings().first()

        new_status = (
            "completed"
            if counts["total"] > 0 and counts["done"] >= counts["total"]
            else "in_progress"
        )

        self.db.execute(
            text("""
                UPDATE user_modules
                SET
                    status       = CAST(:status AS user_module_status),
                    completed_at = CASE
                                     WHEN :status = 'completed' THEN now()
                                     ELSE NULL
                                   END
                WHERE user_id = :user_id AND module_id = :module_id
            """),
            {"user_id": user_id, "module_id": module_id, "status": new_status},
        )