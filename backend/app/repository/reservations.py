import datetime
import uuid

from sqlmodel import Session, exists, func, select

from app.models.reservations import Reservation, ReservationCreate
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
        stmt = (
            select(Reservation.tryout_id)
            .where(Reservation.user_id == user_id)
            .where(Reservation.tryout_id.in_(tryout_ids))
        )
        return set(self.session.exec(stmt).all())

    def has_overlapping_reservation(
        self, user_id: int, start_time: datetime, end_time: datetime
    ) -> bool:
        stmt = select(
            exists().where(
                Reservation.user_id == user_id,
                Tryout.start_time < end_time,
                Tryout.end_time > start_time,
            )
        )
        return bool(self.session.exec(stmt).first())

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
        return self.session.exec(stmt).all()

    def get_by_id(self, id: int) -> Reservation:
        return self.session.get(Reservation, id)
