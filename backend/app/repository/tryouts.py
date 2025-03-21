from sqlmodel import Session, select

from app.models.tryouts import Tryout, TryoutCreate


class TryoutRepository:
    def __init__(self, session: Session):
        self.session = session

    def create(self, tryouts_create: TryoutCreate) -> Tryout:
        tryout = Tryout.model_validate(tryouts_create)
        self.session.add(tryout)
        self.session.commit()
        self.session.refresh(tryout)
        return tryout

    def list_upcoming(self, now, limit=20, offset=0):
        stmt = (
            select(Tryout)
            .where(Tryout.start_time > now)
            .order_by(Tryout.start_time)
            .offset(offset)
            .limit(limit)
        )
        return self.session.exec(stmt).all()
