from datetime import datetime, timedelta

from sqlmodel import Session, create_engine

from app.core.config import settings
from app.models.tryouts import TryoutCreate
from app.models.users import UserCreate
from app.repository.tryouts import TryoutRepository
from app.repository.users import UserRepository

engine = create_engine(str(settings.SQLALCHEMY_DATABASE_URI))


def init_db(session: Session) -> None:
    now = datetime.now()
    user_repo = UserRepository(session=session)
    tryout_repo = TryoutRepository(session=session)

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

        # 3. Create test tryouts
        for i in range(10):
            name = f"Test Tryout {i + 1}"

            if i < 5:
                # 예약 가능한 케이스
                start = now + timedelta(days=10)
                registration_start = start - timedelta(days=1)
            else:
                # 예약 불가능한 케이스
                start = now + timedelta(days=2)

            registration_start = start - timedelta(days=10)
            registration_end = start - timedelta(days=3)
            tryout = TryoutCreate(
                name=name,
                start_time=start,
                end_time=start + timedelta(hours=2),
                registration_start_time=registration_start,
                registration_end_time=registration_end,
                max_capacity=50000,
                confirmed_reserved_count=i * 5000,
            )
            tryout_repo.create(tryouts_create=tryout)
