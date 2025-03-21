from datetime import datetime

from sqlmodel import Field, SQLModel


class ExamBase(SQLModel):
    start_time: datetime
    end_time: datetime
    max_capacity: int = Field(ge=0)
    confirmed_reserved_count: int = Field(ge=0, default=0)


class ExamCreate(ExamBase):
    pass


class Exam(ExamBase, table=True):
    __tablename__ = "exams"
    id: int = Field(default=None, primary_key=True)


class ExamPublic(ExamBase):
    id: int
