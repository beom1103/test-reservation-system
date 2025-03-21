from sqlmodel import Session, select

from app.models.exams import Exam, ExamCreate


class ExamRepository:
    def __init__(self, session: Session):
        self.session = session

    def create(self, exam_create: ExamCreate) -> Exam:
        exam = Exam.model_validate(exam_create)
        self.session.add(exam)
        self.session.commit()
        self.session.refresh(exam)
        return exam

    def get_by_id(self, exam_id: int) -> Exam | None:
        return self.session.get(Exam, exam_id)

    def list(self, skip: int = 0, limit: int = 100) -> list[Exam]:
        statement = select(Exam).offset(skip).limit(limit)
        return self.session.exec(statement).all()
