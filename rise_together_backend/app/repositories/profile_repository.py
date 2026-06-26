"""
ProfileRepository

Implements the user_profile_view as a Python method rather than a SQL view
because education, experience, and skills are variable-length arrays that
are cleaner to assemble in Python than with json_agg.

Returns:
    {
        "user":         {},
        "profile":      {},
        "education":    [],
        "experience":   [],
        "skills":       [],
        "profileLinks": []
    }
"""

from sqlalchemy import text
from sqlalchemy.orm import Session


class ProfileRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_full_profile(self, user_id: int, public: bool = False) -> dict | None:
        """
        Returns the full profile for a user.
        If public=True, the email field is stripped from the user object.
        Returns None if user doesn't exist.
        """
        # 1. User + profile (left join so missing profile still returns the user)
        user_row = self.db.execute(
            text("""
                SELECT
                    u.id, u.name, u.email, u.role, u.created_at,
                    up.headline, up.bio
                FROM users u
                LEFT JOIN user_profiles up ON up.user_id = u.id
                WHERE u.id = :user_id
            """),
            {"user_id": user_id},
        ).mappings().first()

        if not user_row:
            return None

        user_row = dict(user_row)

        user = {
            "id":         user_row["id"],
            "name":       user_row["name"],
            "role":       user_row["role"],
            "created_at": user_row["created_at"],
        }
        if not public:
            user["email"] = user_row["email"]

        profile = {
            "headline": user_row["headline"],
            "bio":      user_row["bio"],
        }

        # 2. Education — most recent first
        education_rows = self.db.execute(
            text("""
                SELECT id, institution, degree, field_of_study,
                       start_date, end_date, description
                FROM education
                WHERE user_id = :user_id
                ORDER BY start_date DESC NULLS LAST
            """),
            {"user_id": user_id},
        ).mappings().all()

        # 3. Experience — most recent first
        experience_rows = self.db.execute(
            text("""
                SELECT id, company, role, description,
                       start_date, end_date
                FROM experience
                WHERE user_id = :user_id
                ORDER BY start_date DESC NULLS LAST
            """),
            {"user_id": user_id},
        ).mappings().all()

        # 4. Skills
        skill_rows = self.db.execute(
            text("""
                SELECT s.id, s.name, s.slug
                FROM skills s
                JOIN user_skills us ON us.skill_id = s.id
                WHERE us.user_id = :user_id
                ORDER BY s.name ASC
            """),
            {"user_id": user_id},
        ).mappings().all()

        # 5. Profile links (GitHub, portfolio, etc.)
        link_rows = self.db.execute(
            text("""
                SELECT l.id, l.title, l.url, l.link_type, l.description
                FROM links l
                JOIN user_profile_links upl ON upl.link_id = l.id
                WHERE upl.user_id = :user_id
            """),
            {"user_id": user_id},
        ).mappings().all()

        return {
            "user":         user,
            "profile":      profile,
            "education":    [dict(r) for r in education_rows],
            "experience":   [dict(r) for r in experience_rows],
            "skills":       [dict(r) for r in skill_rows],
            "profileLinks": [dict(r) for r in link_rows],
        }