from sqlmodel import Session, select

from app.core.security import get_password_hash, verify_password
from app.models.users import User, UserCreate


class UserRepository:
    def __init__(self, session: Session):
        self.session = session

    def create(self, user_create: UserCreate) -> User:
        db_obj = User.model_validate(
            user_create,
            update={"hashed_password": get_password_hash(user_create.password)},
        )
        self.session.add(db_obj)
        self.session.commit()
        self.session.refresh(db_obj)
        return db_obj

    def get_user_by_email(self, email: str) -> User | None:
        statement = select(User).where(User.email == email)
        session_user = self.session.exec(statement).first()
        return session_user

    def authenticate(self, email: str, password: str) -> User | None:
        db_user = self.get_user_by_email(self=self.session, email=email)
        if not db_user:
            return None
        if not verify_password(password, db_user.hashed_password):
            return None
        return db_user
