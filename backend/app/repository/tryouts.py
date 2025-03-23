from sqlmodel import Session, func, select

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

    def get_by_id(self, tryout_id: int, for_update: bool = False) -> Tryout | None:
        if for_update:
            stmt = select(Tryout).where(Tryout.id == tryout_id).with_for_update()
            return self.session.exec(stmt).first()
        return self.session.get(Tryout, tryout_id)

    def paginate_upcoming(self, now, limit=20, offset=0) -> list[Tryout]:
        stmt = (
            select(Tryout)
            .where(Tryout.start_time > now)
            .order_by(Tryout.id)
            .order_by(Tryout.start_time)
            .offset(offset)
            .limit(limit)
        )
        return self.session.exec(stmt).all()

    def count_upcoming(self, now) -> int:
        stmt = select(func.count()).select_from(Tryout).where(Tryout.start_time > now)
        return self.session.exec(stmt).one()
