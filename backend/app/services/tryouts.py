from datetime import datetime

from sqlmodel import Session

from app.core.exceptions import (
    TryoutNotFoundError,
)
from app.core.transaction import TransactionHelper
from app.models.common import PaginatedResponse
from app.models.reservations import Reservation, ReservationCreate
from app.models.tryouts import TryoutPublic
from app.repository.tryouts import TryoutRepository
from app.services.reservations import ReservationService


class TryoutService:
    def __init__(self, session: Session):
        self.reservation_service = ReservationService(session)
        self.repo = TryoutRepository(session)

    def get_tryout_by_id(self, tryout_id: int, user_id: int) -> TryoutPublic:
        tryout = self.repo.get_by_id(tryout_id)
        if not tryout:
            from fastapi import HTTPException

            raise HTTPException(status_code=404, detail="Tryout not found")

        reserved_ids = self.reservation_service.repo.get_user_reserved_tryout_ids(
            user_id=user_id, tryout_ids=[tryout_id]
        )

        return TryoutPublic(
            **tryout.model_dump(), isApplied=(tryout_id in reserved_ids)
        )

    def paginate_upcoming_tryouts(
        self, user_id: int, limit: int, offset: int
    ) -> PaginatedResponse[TryoutPublic]:
        now = datetime.now()
        tryouts = self.repo.paginate_upcoming(now=now, limit=limit, offset=offset)
        total = self.repo.count_upcoming(now=now)

        tryout_ids = [t.id for t in tryouts]
        reserved_ids = self.reservation_service.repo.get_user_reserved_tryout_ids(
            user_id=user_id, tryout_ids=tryout_ids
        )

        items = [
            TryoutPublic(**t.model_dump(), isApplied=(t.id in reserved_ids))
            for t in tryouts
        ]

        return PaginatedResponse[TryoutPublic](
            total=total,
            items=items,
        )

    def reserve_tryout(
        self, user_id: int, tryout_id: int, reserved_seats: int = 1
    ) -> Reservation:
        def operation():
            tryout = self.repo.get_by_id(tryout_id, for_update=True)
            if not tryout:
                raise TryoutNotFoundError()

            self.reservation_service.validate_reservation_or_raise(
                tryout, user_id, reserved_seats, datetime.now()
            )

            reservation_in = ReservationCreate(
                user_id=user_id,
                tryout_id=tryout_id,
                reserved_seats=reserved_seats,
            )

            return self.reservation_service.repo.create(reservation_in)

        return TransactionHelper(self.repo.session).run(operation)
