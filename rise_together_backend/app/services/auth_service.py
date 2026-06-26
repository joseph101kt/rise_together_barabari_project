from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.core.security import create_access_token, hash_password, verify_password
from app.repositories.user_repository import UserRepository
from app.schemas.auth import LoginRequest, RegisterRequest, TokenResponse


class AuthService:
    def __init__(self, db: Session):
        self.user_repo = UserRepository(db)
        self.db = db

    def register(self, request: RegisterRequest) -> TokenResponse:
        if self.user_repo.get_by_email(request.email):
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="An account with that email already exists",
            )

        user = self.user_repo.create(
            name=request.name,
            email=request.email,
            password_hash=hash_password(request.password),
        )
        self.db.commit()

        return TokenResponse(access_token=create_access_token(user.id))

    def login(self, request: LoginRequest) -> TokenResponse:
        user = self.user_repo.get_by_email(request.email)

        if user is None or not verify_password(request.password, user.password_hash):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password",
                headers={"WWW-Authenticate": "Bearer"},
            )

        return TokenResponse(access_token=create_access_token(user.id))