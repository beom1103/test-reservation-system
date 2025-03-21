from datetime import datetime, timedelta

from sqlmodel import Session, create_engine

from app.core.config import settings
from app.models.exams import ExamCreate
from app.models.users import UserCreate
from app.repository.exams import ExamRepository
from app.repository.users import UserRepository

engine = create_engine(str(settings.SQLALCHEMY_DATABASE_URI))


def init_db(session: Session) -> None:
    now = datetime.now()
    user_repo = UserRepository(session=session)
    exam_repo = ExamRepository(session=session)

    admin = user_repo.get_user_by_email(settings.FIRST_SUPERUSER)

    if not admin:
        # 1. Create admin
        admin_in = UserCreate(
            email=settings.FIRST_SUPERUSER,
            password=settings.FIRST_SUPERUSER_PASSWORD,
            is_superuser=True,
        )
        admin = user_repo.create(user_create=admin_in)

        # 2. Create test users
        for i in range(10):
            email = f"user{i}@example.com"
            user_in = UserCreate(
                email=email,
                password="password123",
                is_superuser=False,
                name=f"User {i}",
            )
            user_repo.create(user_create=user_in)

        # 3. Create test exams
        for i in range(10):
            start = now + timedelta(days=5 + i)
            end = start + timedelta(hours=2)
            exam = ExamCreate(
                start_time=start,
                end_time=end,
                max_capacity=50000,
            )
            exam_repo.create(exam_create=exam)
