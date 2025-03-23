import datetime

from sqlmodel import Session, exists, select

from app.models.reservations import Reservation, ReservationCreate
from app.models.tryouts import Tryout


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
        self, user_id: int, tryout_ids: list[int]
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
        return self.session.exec(stmt).first()
