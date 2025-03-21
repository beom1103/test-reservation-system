from datetime import datetime

from sqlmodel import Session

from app.models.tryouts import TryoutPublic
from app.repository.reservations import ReservationRepository
from app.repository.tryouts import TryoutRepository


class TryoutService:
    def __init__(self, session: Session):
        self.repo = TryoutRepository(session)
        self.reservation_repo = ReservationRepository(session)

    def get_tryout_by_id(self, tryout_id: int, user_id: int) -> TryoutPublic:
        tryout = self.repo.get_by_id(tryout_id)
        if not tryout:
            from fastapi import HTTPException

            raise HTTPException(status_code=404, detail="Tryout not found")

        reserved_ids = self.reservation_repo.get_user_reserved_tryout_ids(
            user_id=user_id, tryout_ids=[tryout_id]
        )

        return TryoutPublic(
            **tryout.model_dump(), isApplied=(tryout_id in reserved_ids)
        )

    def get_upcoming_tryouts(
        self, user_id: int, limit: int, offset: int
    ) -> list[TryoutPublic]:
        now = datetime.now()
        tryouts = self.repo.list_upcoming(now=now, limit=limit, offset=offset)

        result = []
        if not tryouts:
            return result

        tryout_ids = [t.id for t in tryouts]

        reserved_ids = self.reservation_repo.get_user_reserved_tryout_ids(
            user_id=user_id, tryout_ids=tryout_ids
        )

        for t in tryouts:
            result.append(
                TryoutPublic(**t.model_dump(), isApplied=(t.id in reserved_ids))
            )
        return result
