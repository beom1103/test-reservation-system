import uuid

from sqlalchemy import UniqueConstraint
from sqlmodel import Enum, Field, SQLModel


class ReservationStatus(str, Enum):
    pending = "pending"
    confirmed = "confirmed"
    cancelled = "cancelled"


class ReservationBase(SQLModel):
    user_id: uuid.UUID = Field(foreign_key="users.id")
    exam_id: int = Field(foreign_key="exams.id")
    reserved_seats: int = Field(ge=1)
    status: ReservationStatus = Field(default=ReservationStatus.pending)
    model_config = {"arbitrary_types_allowed": True}


class ReservationCreate(ReservationBase):
    pass


class Reservation(ReservationBase, table=True):
    __tablename__ = "reservations"
    id: int = Field(default=None, primary_key=True)
    __table_args__ = (UniqueConstraint("user_id", "exam_id", name="uq_user_exam"),)


class ReservationPublic(ReservationBase):
    id: int
