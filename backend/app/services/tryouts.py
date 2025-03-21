from datetime import datetime

from sqlmodel import Session

from app.models.tryouts import TryoutPublic
from app.repository.reservations import ReservationRepository
from app.repository.tryouts import TryoutRepository


class TryoutService:
    def __init__(self, session: Session):
        self.repo = TryoutRepository(session)
        self.reservation_repo = ReservationRepository(session)

    def get_upcoming_tryouts(
        self, user_id: int, limit: int, offset: int
    ) -> list[TryoutPublic]:
        now = datetime.now()
        tryouts = self.repo.list_upcoming(now=now, limit=limit, offset=offset)

        tryout_ids = [t.id for t in tryouts]

        reserved_ids = self.reservation_repo.get_user_reserved_tryout_ids(
            user_id=user_id, tryout_ids=tryout_ids
        )

        result = []
        for t in tryouts:
            result.append(
                TryoutPublic(**t.model_dump(), isApplied=(t.id in reserved_ids))
            )
        return result
