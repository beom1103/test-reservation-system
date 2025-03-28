import uuid
from datetime import datetime

from sqlalchemy import and_, exists, func
from sqlmodel import Session, col, select

from app.core.exceptions import NotFoundError
from app.models.reservations import (
    Reservation,
    ReservationCreate,
    ReservationStatus,
    ReservationUpdate,
)
from app.models.tryouts import Tryout
from app.models.users import User


class ReservationRepository:
    def __init__(self, session: Session):
        self.session = session

    def create(self, reservation_create: ReservationCreate) -> Reservation:
        reservation = Reservation.model_validate(reservation_create)
        self.session.add(reservation)
        self.session.commit()
        self.session.refresh(reservation)
        return reservation

    def get_user_reserved_tryout_ids(
        self, user_id: uuid.UUID, tryout_ids: list[int]
    ) -> set[int]:
        stmt = select(Reservation.tryout_id).where(
            and_(
                col(Reservation.user_id) == user_id,
                col(Reservation.tryout_id).in_(tryout_ids),
                col(Reservation.status) != ReservationStatus.deleted,
            )
        )
        return set(self.session.exec(stmt).all())

    def has_overlapping_reservation(
        self, user_id: uuid.UUID, start_time: datetime, end_time: datetime
    ) -> bool:
        stmt = select(
            exists().where(
                and_(
                    col(Reservation.user_id) == user_id,
                    col(Tryout.start_time) < end_time,
                    col(Tryout.end_time) > start_time,
                    col(Reservation.status) != ReservationStatus.deleted,
                )
            )
        )
        result = self.session.exec(stmt).one()
        return bool(result)

    def count_user_reservations(self, user: User) -> int:
        stmt = select(func.count()).select_from(Reservation)
        if not user.is_superuser:
            stmt = stmt.where(Reservation.user_id == user.id)
        return self.session.exec(stmt).one()

    def paginate_user_reservations(
        self, user: User, limit: int, offset: int
    ) -> list[Reservation]:
        stmt = select(Reservation)
        if not user.is_superuser:
            stmt = stmt.where(Reservation.user_id == user.id)
        stmt = stmt.offset(offset).limit(limit)
        return list(self.session.exec(stmt).all())

    def get_by_id(self, id: int, for_update: bool = False) -> Reservation:
        result = self.session.get(Reservation, id, with_for_update=for_update)
        if not result:
            raise NotFoundError(f"예약을 찾을 수 없습니다. (id:${id} )")
        return result

    def update(
        self, reservation: Reservation, update_data: ReservationUpdate
    ) -> Reservation:
        if update_data.reserved_seats is not None:
            reservation.reserved_seats = update_data.reserved_seats

        if update_data.status is not None:
            reservation.status = update_data.status

        self.session.add(reservation)
        self.session.commit()
        self.session.refresh(reservation)
        return reservation

    def get_by_user_and_tryout(
        self, user_id: uuid.UUID, tryout_id: int, for_update: bool = False
    ) -> Reservation | None:
        stmt = select(Reservation).where(
            and_(
                col(Reservation.user_id) == user_id,
                col(Reservation.tryout_id) == tryout_id,
            )
        )
        if for_update:
            stmt = stmt.with_for_update()

        return self.session.exec(stmt).first()
