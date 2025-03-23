import uuid
from enum import Enum

from pydantic import BaseModel
from sqlalchemy import UniqueConstraint
from sqlmodel import Field, SQLModel


class ReservationStatus(str, Enum):
    pending = "pending"
    confirmed = "confirmed"
    deleted = "deleted"


class ReservationBase(SQLModel):
    user_id: uuid.UUID = Field(foreign_key="users.id")
    tryout_id: int = Field(foreign_key="tryouts.id")
    reserved_seats: int = Field(ge=1)
    status: str = Field(default=ReservationStatus.pending)
    model_config = {"from_attributes": True}


class ReservationCreate(ReservationBase):
    pass


class Reservation(ReservationBase, table=True):
    __tablename__ = "reservations"
    id: int = Field(default=None, primary_key=True)
    __table_args__ = (UniqueConstraint("user_id", "tryout_id", name="uq_user_tryout"),)


class ReservationPublic(ReservationBase):
    id: int


class ReservationUpdate(BaseModel):
    status: str | None = Field(default=None, description="변경할 예약 상태")
    reserved_seats: int | None = Field(
        default=None, ge=1, le=50000, description="변경할 응시 인원 수"
    )


class ReservationUpdateRequest(BaseModel):
    reserved_seats: int = Field(
        default=None, ge=1, le=50000, description="변경할 응시 인원 수"
    )
