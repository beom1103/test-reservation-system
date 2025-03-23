import uuid
from datetime import datetime

from sqlmodel import Session

from app.core.exceptions import (
    AlreadyReservedError,
    AuthorizationError,
    BadRequestError,
    InvalidReservationPeriodError,
    ReservationNotFoundError,
    TryoutFullError,
    TryoutNotFoundError,
)
from app.core.transaction import TransactionHelper
from app.models.common import PaginatedResponse
from app.models.reservations import (
    Reservation,
    ReservationStatus,
    ReservationUpdateRequest,
)
from app.models.tryouts import Tryout, TryoutUpdateRequest
from app.models.users import User
from app.repository.reservations import ReservationRepository
from app.repository.tryouts import TryoutRepository


class ReservationService:
    def __init__(self, session: Session):
        self.session = session
        self.repo = ReservationRepository(session)
        self.tryout_repo = TryoutRepository(session)

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

    def reject_reservation(
        self, reservation_id: int, current_user: User
    ) -> Reservation:
        return self.__update_status(
            reservation_id=reservation_id,
            new_status=ReservationStatus.cancelled,
            current_user=current_user,
            adjust_capacity=False,
        )

    def confirm_reservation(
        self, reservation_id: int, current_user: User
    ) -> Reservation:
        return self.__update_status(
            reservation_id=reservation_id,
            new_status=ReservationStatus.confirmed,
            current_user=current_user,
            adjust_capacity=True,
        )

    def __update_status(
        self,
        reservation_id: int,
        new_status: str,
        current_user: User,
        adjust_capacity: bool,
    ) -> Reservation:
        if not current_user.is_superuser:
            raise AuthorizationError("어드민만 예약 상태를 변경할 수 있습니다.")

        def operation():
            reservation = self.repo.get_by_id(reservation_id, for_update=True)
            if not reservation:
                raise ReservationNotFoundError()

            if reservation.status != ReservationStatus.pending:
                raise BadRequestError("이미 확정되었거나 취소된 예약입니다.")

            tryout = self.tryout_repo.get_by_id(reservation.tryout_id, for_update=True)

            if not tryout:
                raise TryoutNotFoundError()

            if adjust_capacity:
                if (
                    tryout.confirmed_reserved_count + reservation.reserved_seats
                    > tryout.max_capacity
                ):
                    raise TryoutFullError()

                tryout_update = TryoutUpdateRequest(
                    confirmed_reserved_count=tryout.confirmed_reserved_count
                    + reservation.reserved_seats
                )
                self.tryout_repo.update(tryout, tryout_update)

            update_data = ReservationUpdateRequest(status=new_status)
            self.repo.update(reservation, update_data)

            return reservation

        return TransactionHelper(self.session).run(operation)
