"""
Seed script for development.
Run from the project root (where main.py lives):

    python -m scripts.seed

Safe to run multiple times — uses get-or-create patterns.
"""


import app.models  # noqa: F401 — must import before create_all
from app.core.database import Base, SessionLocal, engine
from app.models.education import Education
from app.models.enums import LinkType, ModuleType, UserRole
from app.models.link import Link
from app.models.module import Module
from app.models.module_link import ModuleLink
from app.models.module_skill import ModuleSkill
from app.models.skill import Skill, UserSkill
from app.models.user import User
from app.models.user_profile import UserProfile
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def get_or_create(db, model, filter_by: dict, defaults: dict = None):
    instance = db.query(model).filter_by(**filter_by).first()
    if instance:
        return instance, False
    data = {**filter_by, **(defaults or {})}
    instance = model(**data)
    db.add(instance)
    db.flush()
    return instance, True


def seed():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()

    try:
        print("Seeding skills...")
        skill_data = [
            ("Python",          "python"),
            ("FastAPI",         "fastapi"),
            ("SQL",             "sql"),
            ("Git",             "git"),
            ("HTML & CSS",      "html-css"),
            ("JavaScript",      "javascript"),
            ("Problem Solving", "problem-solving"),
            ("Communication",   "communication"),
            ("Resume Writing",  "resume-writing"),
            ("LinkedIn",        "linkedin"),
        ]
        skills = {}
        for name, slug in skill_data:
            skill, created = get_or_create(db, Skill, {"slug": slug}, {"name": name})
            skills[slug] = skill
            if created:
                print(f"  + skill: {name}")

        print("\nSeeding demo user...")
        user, created = get_or_create(
            db,
            User,
            {"email": "priya@example.com"},
            {
                "name": "Priya Sharma",
                "password_hash": pwd_context.hash("password123"),
                "role": UserRole.learner,
            },
        )
        if created:
            print("  + user: Priya Sharma (priya@example.com / password123)")

            db.add(UserProfile(
                user_id=user.id,
                headline="CS student at Govt Engineering College, Nagpur",
                bio="First-gen tech student trying to break into the industry.",
            ))

            db.add(Education(
                user_id=user.id,
                institution="Government Engineering College, Nagpur",
                degree="B.E.",
                field_of_study="Computer Science",
            ))

            for slug in ["python", "html-css", "git"]:
                db.add(UserSkill(user_id=user.id, skill_id=skills[slug].id))

        admin, created = get_or_create(
            db,
            User,
            {"email": "admin@risetogether.in"},
            {
                "name": "Rise Together Admin",
                "password_hash": pwd_context.hash("admin123"),
                "role": UserRole.admin,
            },
        )
        if created:
            print("  + user: Admin (admin@risetogether.in / admin123)")

        print("\nSeeding modules...")

        # Root path
        path, created = get_or_create(
            db,
            Module,
            {"title": "Getting Job-Ready", "parent_id": None},
            {
                "module_type": ModuleType.path,
                "description": "Everything you need to land your first tech job.",
                "estimated_completion_time": "8 weeks",
                "created_by": admin.id,
                "order_index": 0,
            },
        )
        if created:
            print("  + path: Getting Job-Ready")

        # Child module 1
        mod1, created = get_or_create(
            db,
            Module,
            {"title": "Build Your Online Presence", "parent_id": path.id},
            {
                "module_type": ModuleType.module,
                "description": "Set up your GitHub and LinkedIn so recruiters can find you.",
                "estimated_completion_time": "3 days",
                "created_by": admin.id,
                "order_index": 0,
            },
        )
        if created:
            print("  + module: Build Your Online Presence")
            db.flush()

            link1 = Link(
                title="How to Write a Great GitHub README",
                url="https://docs.github.com/en/repositories/managing-your-repositorys-settings-and-features/customizing-your-repository/about-readmes",
                link_type=LinkType.resources,
                created_by=admin.id,
            )
            db.add(link1)
            db.flush()
            db.add(ModuleLink(module_id=mod1.id, link_id=link1.id, order_index=0))
            db.add(ModuleSkill(module_id=mod1.id, skill_id=skills["git"].id))
            db.add(ModuleSkill(module_id=mod1.id, skill_id=skills["linkedin"].id))

        # Child module 2
        mod2, created = get_or_create(
            db,
            Module,
            {"title": "Python Fundamentals", "parent_id": path.id},
            {
                "module_type": ModuleType.module,
                "description": "Core Python you actually need for backend work.",
                "estimated_completion_time": "2 weeks",
                "created_by": admin.id,
                "order_index": 1,
            },
        )
        if created:
            print("  + module: Python Fundamentals")
            db.flush()

            link2 = Link(
                title="Python Official Tutorial",
                url="https://docs.python.org/3/tutorial/",
                link_type=LinkType.resources,
                created_by=admin.id,
            )
            db.add(link2)
            db.flush()
            db.add(ModuleLink(module_id=mod2.id, link_id=link2.id, order_index=0))
            db.add(ModuleSkill(module_id=mod2.id, skill_id=skills["python"].id))
            db.add(ModuleSkill(module_id=mod2.id, skill_id=skills["problem-solving"].id))

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