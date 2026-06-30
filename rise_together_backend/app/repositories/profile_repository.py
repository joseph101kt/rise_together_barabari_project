"""
ProfileRepository

Read side: get_full_profile (the user_profile_view equivalent)
Write side: upsert_profile, upsert_education, upsert_experience, upsert_profile_links

Education, experience, and profile links all use a full-replace strategy:
delete the user's existing rows, then bulk-insert the new list.
This keeps the write logic simple for MVP.
"""

from app.models.education import Education
from app.models.experience import Experience
from app.models.enums import LinkType
from app.models.link import Link
from app.models.user_profile import UserProfile
from app.models.user_profile_link import UserProfileLink
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.services.link_services import LinkService


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
                SELECT l.id, l.title, l.url, l.link_type, l.description, l.og_title, l.og_description, l.og_image
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

    # ------------------------------------------------------------------
    # Write side
    # ------------------------------------------------------------------

    def upsert_profile(self, user_id: int, headline: str | None, bio: str | None) -> None:
        """
        Insert or update the user_profiles row for this user.
        Creates the row if it doesn't exist yet.
        """
        existing = self.db.query(UserProfile).filter(UserProfile.user_id == user_id).first()
        if existing:
            existing.headline = headline
            existing.bio = bio
        else:
            self.db.add(UserProfile(user_id=user_id, headline=headline, bio=bio))
        self.db.flush()

    def upsert_education(self, user_id: int, entries: list[dict]) -> None:
        """
        Full replace: deletes all education rows for this user then inserts new ones.
        Each entry dict: { institution, degree?, field_of_study?, start_date?, end_date?, description? }
        Pass an empty list to clear all education.
        """
        self.db.query(Education).filter(Education.user_id == user_id).delete()
        for entry in entries:
            self.db.add(Education(user_id=user_id, **entry))
        self.db.flush()

    def upsert_experience(self, user_id: int, entries: list[dict]) -> None:
        """
        Full replace: deletes all experience rows for this user then inserts new ones.
        Each entry dict: { company, role, description?, start_date?, end_date? }
        Pass an empty list to clear all experience.
        """
        self.db.query(Experience).filter(Experience.user_id == user_id).delete()
        for entry in entries:
            self.db.add(Experience(user_id=user_id, **entry))
        self.db.flush()

    def upsert_profile_links(self, user_id: int, links: list[dict]) -> None:
        """
        Full replace for profile links.

        Existing links are deleted.
        New links automatically fetch Open Graph metadata.
        """

        # Delete old join rows and the link rows they pointed to
        old_joins = (
            self.db.query(UserProfileLink)
            .filter(UserProfileLink.user_id == user_id)
            .all()
        )

        old_link_ids = [join.link_id for join in old_joins]

        self.db.query(UserProfileLink).filter(
            UserProfileLink.user_id == user_id
        ).delete()

        if old_link_ids:
            self.db.query(Link).filter(
                Link.id.in_(old_link_ids)
            ).delete(synchronize_session=False)

        # Create new links
        for link_data in links:
            metadata = LinkService.fetch_metadata(link_data["url"])
            print(metadata)

            link = Link(
                title=link_data["title"],
                url=link_data["url"],
                description=link_data.get("description"),
                link_type=LinkType(link_data["link_type"]),
                created_by=user_id,

                og_title=metadata["og_title"],
                og_description=metadata["og_description"],
                og_image=metadata["og_image"],
                og_fetched_at=metadata["fetched_at"],
            )

            self.db.add(link)
            self.db.flush()

            self.db.add(
                UserProfileLink(
                    user_id=user_id,
                    link_id=link.id,
                )
            )

        self.db.flush()

