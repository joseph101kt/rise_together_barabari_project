"""
Seed script for development.
Reads seed_data.json from the same directory as this file.

Run from the project root:

    python -m app.scripts.seed

Safe to run multiple times — uses get-or-create patterns.
Every link has OG metadata fetched at seed time.
"""

import json
from pathlib import Path

import app.models  # noqa: F401 — registers all models before create_all
from app.core.database import Base, SessionLocal, engine
from app.models.education import Education
from app.models.enums import LinkType, ModuleType, SubLinkType, UserRole
from app.models.link import Link
from app.models.module import Module
from app.models.module_link import ModuleLink
from app.models.module_skill import ModuleSkill
from app.models.skill import Skill, UserSkill
from app.models.user import User
from app.models.user_profile import UserProfile
from app.models.user_profile_link import UserProfileLink
from app.services.link_services import LinkService
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

SEED_FILE = Path(__file__).parent / "seed_data.json"


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def get_or_create(db, model, filter_by: dict, defaults: dict = None):
    instance = db.query(model).filter_by(**filter_by).first()
    if instance:
        return instance, False
    instance = model(**{**filter_by, **(defaults or {})})
    db.add(instance)
    db.flush()
    return instance, True


def make_link(db, *, title: str, url: str, link_type: LinkType, created_by: int, description: str | None = None) -> Link:
    print(f"      fetching OG: {url}")
    metadata = LinkService.fetch_metadata(url)
    link = Link(
        title=title,
        url=url,
        description=description,
        link_type=link_type,
        created_by=created_by,
        og_title=metadata["og_title"],
        og_description=metadata["og_description"],
        og_image=metadata["og_image"],
        og_fetched_at=metadata["fetched_at"],
    )
    db.add(link)
    db.flush()
    return link


# ---------------------------------------------------------------------------
# Section seeders
# ---------------------------------------------------------------------------

def seed_skills(db, skill_data: list[dict]) -> dict[str, Skill]:
    print("Seeding skills...")
    skills: dict[str, Skill] = {}
    for entry in skill_data:
        skill, created = get_or_create(
            db, Skill, {"slug": entry["slug"]}, {"name": entry["name"]}
        )
        skills[entry["slug"]] = skill
        if created:
            print(f"  + {entry['name']}")
    return skills


def seed_users(
    db,
    user_data: list[dict],
    skills: dict[str, Skill],
) -> dict[str, User]:
    print("\nSeeding users...")
    users: dict[str, User] = {}

    for entry in user_data:
        user, created = get_or_create(
            db,
            User,
            {"email": entry["email"]},
            {
                "name": entry["name"],
                "password_hash": pwd_context.hash(entry["password"]),
                "role": UserRole(entry["role"]),
            },
        )
        users[entry["email"]] = user

        if not created:
            continue

        print(f"  + {entry['email']} / {entry['password']}  [{entry['role']}]")

        if profile := entry.get("profile"):
            db.add(UserProfile(
                user_id=user.id,
                headline=profile.get("headline"),
                bio=profile.get("bio"),
            ))

        for edu in entry.get("education", []):
            db.add(Education(
                user_id=user.id,
                institution=edu["institution"],
                degree=edu.get("degree"),
                field_of_study=edu.get("field_of_study"),
                start_date=edu.get("start_date"),
                end_date=edu.get("end_date"),
                description=edu.get("description"),
            ))

        for slug in entry.get("skills", []):
            if slug in skills:
                db.add(UserSkill(user_id=user.id, skill_id=skills[slug].id))
            else:
                print(f"    ! unknown skill slug '{slug}' for user {entry['email']}, skipping")

        for pl in entry.get("profile_links", []):
            link = make_link(
                db,
                title=pl["title"],
                url=pl["url"],
                link_type=LinkType(pl["link_type"]),
                created_by=user.id,
            )
            db.add(UserProfileLink(user_id=user.id, link_id=link.id))

        db.flush()

    return users


def seed_modules(
    db,
    module_data: list[dict],
    skills: dict[str, Skill],
    users: dict[str, User],
    parent_id: int | None = None,
) -> None:
    for entry in module_data:
        created_by_email = entry.get("created_by")
        if created_by_email not in users:
            raise ValueError(
                f"Module '{entry['title']}' references unknown user email '{created_by_email}'. "
                "Make sure that user is listed in the 'users' array."
            )
        creator = users[created_by_email]

        module, created = get_or_create(
            db,
            Module,
            {"title": entry["title"], "parent_id": parent_id},
            {
                "module_type": ModuleType(entry["module_type"]),
                "description": entry.get("description"),
                "estimated_completion_time": entry.get("estimated_completion_time"),
                "created_by": creator.id,
                "order_index": entry.get("order_index", 0),
            },
        )

        indent = "  " if parent_id is None else "    "
        if created:
            print(f"{indent}+ [{entry['module_type']}] {entry['title']}")
            db.flush()

            for link_entry in entry.get("links", []):
                link = make_link(
                    db,
                    title=link_entry["title"],
                    url=link_entry["url"],
                    link_type=LinkType(link_entry["link_type"]),
                    created_by=creator.id,
                )
                sub_link_type = None
                if raw_slt := link_entry.get("sub_link_type"):
                    sub_link_type = SubLinkType(raw_slt)

                db.add(ModuleLink(
                    module_id=module.id,
                    link_id=link.id,
                    order_index=link_entry.get("order_index", 0),
                    sub_link_type=sub_link_type,
                ))

            for slug in entry.get("skills", []):
                if slug in skills:
                    db.add(ModuleSkill(module_id=module.id, skill_id=skills[slug].id))
                else:
                    print(f"      ! unknown skill slug '{slug}' for module '{entry['title']}', skipping")

            db.flush()

        # Recurse into children regardless of whether the parent was just created,
        # so re-runs can still add new child modules.
        if children := entry.get("children"):
            seed_modules(db, children, skills, users, parent_id=module.id)


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

def seed():
    if not SEED_FILE.exists():
        raise FileNotFoundError(
            f"seed_data.json not found at {SEED_FILE}. "
            "Copy seed_data.example.json to seed_data.json and fill it in."
        )

    with SEED_FILE.open() as f:
        data = json.load(f)

    Base.metadata.create_all(bind=engine)
    db = SessionLocal()

    try:
        skills = seed_skills(db, data.get("skills", []))
        users  = seed_users(db, data.get("users", []), skills)

        print("\nSeeding modules...")
        seed_modules(db, data.get("modules", []), skills, users)

        db.commit()
        print("\nSeed complete.")

    except Exception as e:
        db.rollback()
        print(f"\nSeed failed: {e}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    seed()