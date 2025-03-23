from datetime import datetime

from pydantic import BaseModel
from sqlmodel import Field, SQLModel


class TryoutBase(SQLModel):
    name: str
    start_time: datetime
    end_time: datetime
    registration_start_time: datetime
    registration_end_time: datetime
    max_capacity: int = Field(ge=0)
    confirmed_reserved_count: int = Field(ge=0, default=0)


class TryoutCreate(TryoutBase):
    pass


class Tryout(TryoutBase, table=True):
    __tablename__ = "tryouts"
    id: int = Field(default=None, primary_key=True)


class TryoutPublic(TryoutBase):
    id: int
    isApplied: bool


class TryoutUpdateRequest(BaseModel):
    confirmed_reserved_count: int | None = Field(
        default=None, description="확정된 예약 수"
    )
