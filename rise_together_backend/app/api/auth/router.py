from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.models.user import User
from app.schemas.auth import LoginRequest, RegisterRequest, TokenResponse
from app.schemas.users import UserResponse
from app.services.auth_service import AuthService

router = APIRouter(prefix="/auth", tags=["Auth"])


@router.post(
    "/register",
    response_model=TokenResponse,
    status_code=201,
    summary="Register a new account",
)
def register(request: RegisterRequest, db: Session = Depends(get_db)):
    return AuthService(db).register(request)


@router.post(
    "/login",
    response_model=TokenResponse,
    summary="Log in and receive a JWT",
)
def login(request: LoginRequest, db: Session = Depends(get_db)):
    return AuthService(db).login(request)


@router.get(
    "/me",
    response_model=UserResponse,
    summary="Return the authenticated user's basic info",
)
def me(current_user: User = Depends(get_current_user)):
    # current_user is already a User ORM object — return it directly.
    # UserResponse has from_attributes=True so Pydantic reads it off the model.
    return current_user