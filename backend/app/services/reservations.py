import uuid
from datetime import datetime

from sqlmodel import Session

from app.core.exceptions import (
    AlreadyReservedError,
    AuthorizationError,
    BadRequestError,
    InvalidReservationPeriodError,
    TryoutFullError,
)
from app.core.transaction import TransactionHelper
from app.models.common import PaginatedResponse
from app.models.reservations import (
    Reservation,
    ReservationStatus,
    ReservationUpdate,
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

    def _validate_confirm_reservation(
        self, reservation: Reservation, tryout: Tryout
    ) -> None:
        if reservation.status != ReservationStatus.pending:
            raise BadRequestError("이미 확정되었거나 삭제된 예약입니다.")

        if tryout.start_time <= datetime.now():
            raise BadRequestError("시험 시작 시간이 지난 예약은 확정할 수 없습니다.")

        if (
            tryout.confirmed_reserved_count + reservation.reserved_seats
            > tryout.max_capacity
        ):
            raise TryoutFullError()

    def _validate_delete_reservation(
        self, reservation: Reservation, tryout: Tryout, current_user: User
    ) -> None:
        is_admin = current_user.is_superuser

        if not is_admin and reservation.status != ReservationStatus.pending:
            raise BadRequestError("확정된 예약은 삭제할 수 없습니다.")

        if not is_admin and reservation.user_id != current_user.id:
            raise AuthorizationError("본인 예약만 삭제할 수 있습니다.")

        if reservation.status == ReservationStatus.deleted:
            raise BadRequestError("이미 삭제된 예약입니다.")

        if tryout.start_time <= datetime.now():
            raise BadRequestError("시험 시작 이후에는 예약을 삭제할 수 없습니다.")

        if reservation.status == ReservationStatus.confirmed and (
            tryout.confirmed_reserved_count < reservation.reserved_seats
        ):
            raise BadRequestError("확정 인원 수가 잘못되었습니다.")

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

        if not current_user.is_superuser and reservation.user_id != current_user.id:
            raise AuthorizationError("접근 권한이 없습니다.")

        return Reservation.model_validate(reservation)

    def confirm_reservation(
        self,
        reservation_id: int,
    ) -> Reservation:
        def operation():
            reservation = self.repo.get_by_id(reservation_id, for_update=True)
            tryout = self.tryout_repo.get_by_id(reservation.tryout_id, for_update=True)

            self._validate_confirm_reservation(reservation, tryout)

            updated_count = tryout.confirmed_reserved_count + reservation.reserved_seats
            tryout_update = TryoutUpdateRequest(confirmed_reserved_count=updated_count)

            update_data = ReservationUpdate(status=ReservationStatus.confirmed)

            self.tryout_repo.update(tryout, tryout_update)
            self.repo.update(reservation, update_data)

            return reservation

        return TransactionHelper(self.session).run(operation)

    def delete_reservation(
        self, reservation_id: int, current_user: User
    ) -> Reservation:
        def operation():
            reservation = self.repo.get_by_id(reservation_id, for_update=True)
            tryout = self.tryout_repo.get_by_id(reservation.tryout_id, for_update=True)

            self._validate_delete_reservation(reservation, tryout, current_user)

            if reservation.status == ReservationStatus.confirmed:
                updated_count = (
                    tryout.confirmed_reserved_count - reservation.reserved_seats
                )
                tryout_update = TryoutUpdateRequest(
                    confirmed_reserved_count=updated_count
                )
                self.tryout_repo.update(tryout, tryout_update)

            reservation_update = ReservationUpdate(status=ReservationStatus.deleted)
            self.repo.update(reservation, reservation_update)

            return reservation

        return TransactionHelper(self.session).run(operation)

    def update_reservation(
        self,
        user: User,
        reservation_id: int,
        update_data: ReservationUpdate,
    ) -> Reservation:
        def operation():
            reservation = self.repo.get_by_id(reservation_id, for_update=True)
            tryout = self.tryout_repo.get_by_id(reservation.tryout_id, for_update=True)
            now = datetime.now()

            self.__validate_update_reservation(
                user, reservation, update_data, tryout, now
            )

            new_seats = update_data.reserved_seats
            diff = new_seats - reservation.reserved_seats
            if reservation.status == ReservationStatus.confirmed:
                tryout_update = TryoutUpdateRequest(
                    confirmed_reserved_count=tryout.confirmed_reserved_count + diff
                )
                self.tryout_repo.update(tryout, tryout_update)

            return self.repo.update(
                reservation, ReservationUpdate(reserved_seats=new_seats)
            )

        return TransactionHelper(self.session).run(operation)

    def __validate_update_reservation(
        self,
        user: User,
        reservation: Reservation,
        update_data: ReservationUpdate,
        tryout: Tryout,
        now: datetime,
    ) -> None:
        if not user.is_superuser and reservation.user_id != user.id:
            raise AuthorizationError("본인 예약만 수정할 수 있습니다.")

        if reservation.status == ReservationStatus.deleted:
            raise BadRequestError("삭제된 예약은 수정할 수 없습니다.")

        if not user.is_superuser and reservation.status == ReservationStatus.confirmed:
            raise BadRequestError("확정된 예약은 수정할 수 없습니다.")

        if tryout.start_time <= now:
            raise BadRequestError("시험 시작 이후에는 예약을 수정할 수 없습니다.")

        if (
            update_data.reserved_seats is None
            or update_data.reserved_seats == reservation.reserved_seats
        ):
            raise BadRequestError("변경된 데이터가 없습니다.")

        new_seats = update_data.reserved_seats
        diff = new_seats - reservation.reserved_seats
        if diff > 0 and tryout.confirmed_reserved_count + diff > tryout.max_capacity:
            raise TryoutFullError("최대 예약 인원을 초과할 수 없습니다.")
