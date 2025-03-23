from datetime import datetime

from backend.app.core.exceptions import NotFoundError
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

    def get_by_id(self, id: int, for_update: bool = False) -> Tryout | None:
        result = self.session.get(Tryout, id, with_for_update=for_update)

        if not result:
            raise NotFoundError(f"예약을 찾을 수 없습니다. (id: ${id})")

        return result

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
