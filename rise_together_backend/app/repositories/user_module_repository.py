"""
UserModuleRepository

Handles all reads and writes for user_modules and user_module_links.

Public methods
--------------
  get_user_modules(user_id)
  get_user_module(user_id, module_id)
  create_user_module(user_id, module_id)
  create_user_module_link(user_id, module_id, module_link_id, url, title)
  patch_user_module_link(user_id, module_id, module_link_id, completed)

OG metadata
-----------
On every read, submitted links with og_title IS NULL are refreshed in-place.
"""

from datetime import datetime

from sqlalchemy import text
from sqlalchemy.orm import Session

from app.services.link_services import LinkService


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

        links_by_module: dict[int, list[dict]] = {}
        for row in link_rows:
            mid = row["module_id"]
            links_by_module.setdefault(mid, []).append(row)

        result = []
        for row in um_rows:
            entry = dict(row)
            entry["submitted_links"] = links_by_module.get(row["module_id"], [])
            result.append(entry)

        return result

    def get_user_module(self, user_id: int, module_id: int) -> dict | None:
        """One user_module with submitted links, or None."""
        self._sync_module_status(user_id, module_id)

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
        entry["submitted_links"] = link_rows
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
        Automatically fetches Open Graph metadata for the submitted URL.
        """
        slot = self.db.execute(
            text("""
                SELECT id
                FROM module_links
                WHERE id = :module_link_id
                AND module_id = :module_id
            """),
            {"module_link_id": module_link_id, "module_id": module_id},
        ).first()

        if slot is None:
            raise ValueError(
                f"module_link {module_link_id} does not belong to module {module_id}."
            )

        existing = self.db.execute(
            text("""
                SELECT 1
                FROM user_module_links
                WHERE user_id = :user_id
                AND module_link_id = :module_link_id
            """),
            {"user_id": user_id, "module_link_id": module_link_id},
        ).first()

        if existing:
            raise ValueError(
                f"User {user_id} already has a submission for slot {module_link_id}."
            )

        metadata = LinkService.fetch_metadata(url)

        link_row = self.db.execute(
            text("""
                INSERT INTO links (
                    title, url, link_type, created_by,
                    og_title, og_description, og_image, og_fetched_at
                )
                VALUES (
                    :title, :url,
                    CAST('submission' AS link_type),
                    :created_by,
                    :og_title, :og_description, :og_image, :og_fetched_at
                )
                RETURNING id
            """),
            {
                "title":          title,
                "url":            url,
                "created_by":     user_id,
                "og_title":       metadata["og_title"],
                "og_description": metadata["og_description"],
                "og_image":       metadata["og_image"],
                "og_fetched_at":  metadata["fetched_at"],
            },
        ).mappings().first()

        link_id = link_row["id"]

        self.db.execute(
            text("""
                INSERT INTO user_module_links (
                    user_id, module_link_id, link_id, completed
                )
                VALUES (:user_id, :module_link_id, :link_id, false)
            """),
            {
                "user_id":        user_id,
                "module_link_id": module_link_id,
                "link_id":        link_id,
            },
        )

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
                "user_id":        user_id,
                "module_link_id": module_link_id,
                "completed":      completed,
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
    ) -> list[dict]:
        rows = self.db.execute(
            text("""
                SELECT
                    ml.module_id,
                    uml.module_link_id,
                    ml.order_index,
                    ml.sub_link_type,
                    uml.link_id,
                    l.title          AS link_title,
                    l.url            AS link_url,
                    l.link_type,
                    l.og_title,
                    l.og_description,
                    l.og_image,
                    uml.completed,
                    uml.completed_at
                FROM user_module_links uml
                JOIN module_links ml ON ml.id = uml.module_link_id
                JOIN links        l  ON l.id  = uml.link_id
                WHERE uml.user_id  = :user_id
                AND ml.module_id   = ANY(:module_ids)
                ORDER BY ml.module_id ASC, ml.order_index ASC
            """),
            {"user_id": user_id, "module_ids": module_ids},
        ).mappings().all()

        return [self._maybe_refresh_og(dict(row)) for row in rows]

    def _maybe_refresh_og(self, row: dict) -> dict:
        """
        If og_title is missing, fetch OG metadata, persist it, and
        return the row with updated values.
        Skips the network call if og_title is already populated.
        """
        if row.get("og_title"):
            return row

        url = row.get("link_url") or row.get("url")
        if not url:
            return row

        metadata = LinkService.fetch_metadata(url)

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
                "id":             row["link_id"],
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

    def _sync_module_status(self, user_id: int, module_id: int) -> None:
        """
        Synchronize the user's module status.

        A module is completed when the user has submitted a link for every
        module_link slot whose underlying link_type is 'submission'.
        The completed flag on user_module_links is not used for this check.
        """
        counts = self.db.execute(
            text("""
                SELECT
                    COUNT(ml.id)              AS total_required,
                    COUNT(uml.module_link_id) AS submitted
                FROM module_links ml
                JOIN links l
                    ON l.id = ml.link_id
                LEFT JOIN user_module_links uml
                    ON uml.module_link_id = ml.id
                    AND uml.user_id = :user_id
                WHERE
                    ml.module_id = :module_id
                    AND l.link_type = CAST('submission' AS link_type)
            """),
            {"user_id": user_id, "module_id": module_id},
        ).mappings().first()

        total_required = counts["total_required"]
        submitted      = counts["submitted"]

        new_status = (
            "completed"
            if total_required > 0 and submitted == total_required
            else "in_progress"
        )

        completed_at = datetime.utcnow() if new_status == "completed" else None

        self.db.execute(
            text("""
                UPDATE user_modules
                SET
                    status       = CAST(:status AS user_module_status),
                    completed_at = :completed_at
                WHERE
                    user_id    = :user_id
                    AND module_id = :module_id
            """),
            {
                "status":       new_status,
                "completed_at": completed_at,
                "user_id":      user_id,
                "module_id":    module_id,
            },
        )