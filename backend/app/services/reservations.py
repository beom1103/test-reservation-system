import uuid
from datetime import datetime

from sqlmodel import Session

from app.core.exceptions import (
    AlreadyReservedError,
    AuthorizationError,
    InvalidReservationPeriodError,
    ReservationNotFoundError,
    TryoutFullError,
)
from app.models.common import PaginatedResponse
from app.models.reservations import Reservation
from app.models.tryouts import Tryout
from app.models.users import User
from app.repository.reservations import ReservationRepository


class ReservationService:
    def __init__(self, session: Session):
        self.session = session
        self.repo = ReservationRepository(session)

    def validate_reservation_or_raise(
        self, tryout: Tryout, user_id: uuid.UUID, reserved_seats: int, now: datetime
    ) -> None:
        if not (tryout.registration_start_time <= now <= tryout.registration_end_time):
            raise InvalidReservationPeriodError()

        reserved_ids = self.repo.get_user_reserved_tryout_ids(
            user_id=user_id, tryout_ids=[tryout.id]
        )
        if tryout.id in reserved_ids:
            raise AlreadyReservedError()

        if self.repo.has_overlapping_reservation(
            user_id=user_id,
            start_time=tryout.start_time,
            end_time=tryout.end_time,
        ):
            raise AlreadyReservedError("동시간대에 이미 예약된 시험이 존재합니다.")

        if tryout.confirmed_reserved_count + reserved_seats > tryout.max_capacity:
            raise TryoutFullError()

    def paginate_reservations(
        self, user: User, limit: int, offset: int
    ) -> PaginatedResponse[Reservation]:
        total = self.repo.count_user_reservations(user)
        reservations = self.repo.paginate_user_reservations(user, limit, offset)

        return PaginatedResponse[Reservation](
            items=[Reservation.model_validate(r) for r in reservations],
            total=total,
        )

    def get_reservation_by_id(
        self, reservation_id: int, current_user: User
    ) -> Reservation:
        reservation = self.repo.get_by_id(reservation_id)
        if not reservation:
            raise ReservationNotFoundError()

        if not current_user.is_superuser and reservation.user_id != current_user.id:
            raise AuthorizationError("접근 권한이 없습니다.")

        return Reservation.model_validate(reservation)
