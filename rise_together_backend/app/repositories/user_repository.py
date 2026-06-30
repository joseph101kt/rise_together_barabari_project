from sqlalchemy.orm import Session

from app.models.enums import UserRole
from app.models.user import User


class UserRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, user_id: int) -> User | None:
        return self.db.query(User).filter(User.id == user_id).first()

    def get_by_email(self, email: str) -> User | None:
        return self.db.query(User).filter(User.email == email).first()

    def create(
        self,
        name: str,
        email: str,
        password_hash: str,
        role: UserRole = UserRole.learner,
    ) -> User:
        user = User(
            name=name,
            email=email,
            password_hash=password_hash,
            role=role,
        )
        self.db.add(user)
        self.db.flush()   # get user.id without committing
        return user

    def update(self, user_id: int, **fields) -> User | None:
        """
        Update arbitrary columns on the users table.
        Only pass fields that actually exist on the model.
        Returns None if the user doesn't exist.
        """
        user = self.get_by_id(user_id)
        if user is None:
            return None
        for key, value in fields.items():
            setattr(user, key, value)
        self.db.flush()
        return user