"""
ProgressRepository

Implements the user_submissions_view as a Python method.

Submissions are user_module_links where link_type = 'submission'.
Groups them by the module they belong to.

Returns:
    [
        {
            "module":          {},
            "submissionLinks": []
        }
    ]
"""

from sqlalchemy import text
from sqlalchemy.orm import Session


class ProgressRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_user_submissions(self, user_id: int) -> list[dict]:
        """
        Returns all submission-type links the user has added, grouped by module.
        Only includes modules where at least one submission link exists.
        """
        rows = self.db.execute(
            text("""
                SELECT
                    m.id             AS module_id,
                    m.title          AS module_title,
                    m.module_type,
                    m.description    AS module_description,
                    l.id             AS link_id,
                    l.title          AS link_title,
                    l.url,
                    l.link_type,
                    uml.completed,
                    uml.completed_at
                FROM user_module_links uml
                JOIN modules m ON m.id = uml.module_id
                JOIN links   l ON l.id = uml.link_id
                WHERE uml.user_id  = :user_id
                  AND l.link_type  = 'submission'
                ORDER BY m.id ASC, l.id ASC
            """),
            {"user_id": user_id},
        ).mappings().all()

        # Group by module
        modules: dict[int, dict] = {}
        for row in rows:
            mid = row["module_id"]
            if mid not in modules:
                modules[mid] = {
                    "module": {
                        "id":          row["module_id"],
                        "title":       row["module_title"],
                        "module_type": row["module_type"],
                        "description": row["module_description"],
                    },
                    "submissionLinks": [],
                }
            modules[mid]["submissionLinks"].append({
                "id":           row["link_id"],
                "title":        row["link_title"],
                "url":          row["url"],
                "link_type":    row["link_type"],
                "completed":    row["completed"],
                "completed_at": row["completed_at"],
            })

        return list(modules.values())

    def upsert_module_progress(
        self,
        user_id: int,
        module_id: int,
        status: str,
    ) -> dict:
        """
        Upsert a user's progress on a module.
        Auto-sets started_at and completed_at based on status transitions.
        """
        self.db.execute(
            text("""
                INSERT INTO user_modules (user_id, module_id, status, started_at, completed_at)
                VALUES (
                    :user_id,
                    :module_id,
                    :status,
                    CASE WHEN :status IN ('in_progress', 'completed') THEN now() ELSE NULL END,
                    CASE WHEN :status = 'completed' THEN now() ELSE NULL END
                )
                ON CONFLICT (user_id, module_id) DO UPDATE SET
                    status       = EXCLUDED.status,
                    started_at   = CASE
                                     WHEN user_modules.started_at IS NULL
                                      AND EXCLUDED.status IN ('in_progress', 'completed')
                                     THEN now()
                                     ELSE user_modules.started_at
                                   END,
                    completed_at = CASE
                                     WHEN EXCLUDED.status = 'completed' THEN now()
                                     ELSE NULL
                                   END
            """),
            {"user_id": user_id, "module_id": module_id, "status": status},
        )
        self.db.commit()

        row = self.db.execute(
            text("""
                SELECT user_id, module_id, status, started_at, completed_at
                FROM user_modules
                WHERE user_id = :user_id AND module_id = :module_id
            """),
            {"user_id": user_id, "module_id": module_id},
        ).mappings().first()

        return dict(row)

    def upsert_link_progress(
        self,
        user_id: int,
        module_id: int,
        link_id: int,
        completed: bool,
    ) -> dict:
        """
        Upsert a user's completion status on a single link within a module.
        """
        self.db.execute(
            text("""
                INSERT INTO user_module_links (user_id, module_id, link_id, completed, completed_at)
                VALUES (
                    :user_id,
                    :module_id,
                    :link_id,
                    :completed,
                    CASE WHEN :completed THEN now() ELSE NULL END
                )
                ON CONFLICT (user_id, module_id, link_id) DO UPDATE SET
                    completed    = EXCLUDED.completed,
                    completed_at = CASE
                                     WHEN EXCLUDED.completed THEN now()
                                     ELSE NULL
                                   END
            """),
            {
                "user_id":   user_id,
                "module_id": module_id,
                "link_id":   link_id,
                "completed": completed,
            },
        )
        self.db.commit()

        row = self.db.execute(
            text("""
                SELECT user_id, module_id, link_id, completed, completed_at
                FROM user_module_links
                WHERE user_id = :user_id AND module_id = :module_id AND link_id = :link_id
            """),
            {"user_id": user_id, "module_id": module_id, "link_id": link_id},
        ).mappings().first()

        return dict(row)