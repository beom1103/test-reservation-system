import uuid
from datetime import datetime

from sqlmodel import Session

from app.core.exceptions import AuthorizationError, NotFoundError
from app.core.transaction import TransactionHelper
from app.models.common import PaginatedResponse
from app.models.reservations import (
    Reservation,
    ReservationCreate,
    ReservationStatus,
    ReservationUpdate,
)
from app.models.tryouts import TryoutPublic
from app.models.users import User
from app.repository.tryouts import TryoutRepository
from app.services.reservations import ReservationService


class TryoutService:
    def __init__(self, session: Session):
        self.reservation_service = ReservationService(session)
        self.repo = TryoutRepository(session)

    def get_tryout_by_id(self, tryout_id: int, user_id: uuid.UUID) -> TryoutPublic:
        tryout = self.repo.get_by_id(tryout_id)
        if not tryout:
            raise NotFoundError("Tryout not found")

        reserved_ids = self.reservation_service.repo.get_user_reserved_tryout_ids(
            user_id=user_id, tryout_ids=[tryout_id]
        )

        return TryoutPublic(
            **tryout.model_dump(), isApplied=(tryout_id in reserved_ids)
        )

    def paginate_upcoming_tryouts(
        self, user_id: uuid.UUID, limit: int, offset: int
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
        self, user: User, tryout_id: int, reserved_seats: int = 1
    ) -> Reservation:
        if user.is_superuser:
            raise AuthorizationError("Admin은 시험 신청이 불가합니다.")

        def operation() -> Reservation:
            tryout = self.repo.get_by_id(tryout_id, for_update=True)

            self.reservation_service.validate_reservation_or_raise(
                tryout, user.id, reserved_seats, datetime.now()
            )

            existing = self.reservation_service.repo.get_by_user_and_tryout(
                user_id=user.id, tryout_id=tryout_id, for_update=True
            )

            if existing and existing.status == ReservationStatus.deleted:
                update_data = ReservationUpdate(
                    status=ReservationStatus.pending,
                    reserved_seats=reserved_seats,
                )
                return self.reservation_service.repo.update(existing, update_data)

            reservation_in = ReservationCreate(
                user_id=user.id,
                tryout_id=tryout_id,
                reserved_seats=reserved_seats,
            )

            return self.reservation_service.repo.create(reservation_in)

        return TransactionHelper(self.repo.session).run(operation)
