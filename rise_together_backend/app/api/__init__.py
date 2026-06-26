from fastapi import APIRouter

from app.api.auth.router import router as auth_router
from app.api.modules.router import router as modules_router
from app.api.skills.router import router as skills_router
from app.api.users.router import router as users_router

# Single router that main.py mounts at /api/v1
api_router = APIRouter()

api_router.include_router(auth_router)
api_router.include_router(users_router)
api_router.include_router(skills_router)
api_router.include_router(modules_router)