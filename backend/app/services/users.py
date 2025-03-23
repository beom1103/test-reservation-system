from sqlmodel import Session

from app.core.security import verify_password
from app.models.users import User
from app.repository.users import UserRepository


class UserService:
    def __init__(self, session: Session):
        self.repo = UserRepository(session)

    def authenticate(self, email: str, password: str) -> User | None:
        db_user = self.repo.get_user_by_email(email=email)
        if not db_user:
            return None
        if not verify_password(password, db_user.hashed_password):
            return None
        return db_user
