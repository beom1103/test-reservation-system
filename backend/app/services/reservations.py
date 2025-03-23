import datetime

from sqlmodel import Session

from app.core.exceptions import (
    AlreadyReservedError,
    InvalidReservationPeriodError,
    TryoutFullError,
)
from app.models.tryouts import Tryout
from app.repository.reservations import ReservationRepository


class ReservationService:
    def __init__(self, session: Session):
        self.session = session
        self.repo = ReservationRepository(session)

    def validate_reservation_or_raise(
        self, tryout: Tryout, user_id: int, reserved_seats: int, now: datetime
    ) -> None:
        if not (tryout.registration_start_time <= now <= tryout.registration_end_time):
            raise InvalidReservationPeriodError()

        reserved_ids = self.repo.get_user_reserved_tryout_ids(
            user_id=user_id, tryout_ids=[tryout.id]
        )
        if tryout.id in reserved_ids:
            raise AlreadyReservedError()

        if tryout.confirmed_reserved_count + reserved_seats > tryout.max_capacity:
            raise TryoutFullError()
