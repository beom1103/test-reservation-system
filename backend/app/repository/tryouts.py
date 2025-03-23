from datetime import datetime

from sqlmodel import Session, func, select

from app.models.tryouts import Tryout, TryoutCreate, TryoutUpdateRequest


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
        return self.session.get(Tryout, tryout_id, with_for_update=for_update)

    def paginate_upcoming(
        self, now: datetime, limit: int = 20, offset: int = 0
    ) -> list[Tryout]:
        stmt = (
            select(Tryout)
            .where(Tryout.start_time > now)
            .order_by("id", "start_time")
            .offset(offset)
            .limit(limit)
        )
        return list(self.session.exec(stmt).all())

    def count_upcoming(self, now: datetime) -> int:
        stmt = select(func.count()).select_from(Tryout).where(Tryout.start_time > now)
        return self.session.exec(stmt).one()

    def update(self, tryout: Tryout, update_data: TryoutUpdateRequest) -> Tryout:
        if update_data.confirmed_reserved_count is not None:
            tryout.confirmed_reserved_count = update_data.confirmed_reserved_count

        self.session.add(tryout)
        self.session.commit()
        self.session.refresh(tryout)

        return tryout
