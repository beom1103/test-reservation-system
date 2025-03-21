from datetime import datetime

from sqlmodel import Session

from app.repository.tryouts import TryoutRepository


class TryoutService:
    def __init__(self, session: Session):
        self.repo = TryoutRepository(session)

    def get_upcoming_tryouts(self, limit: int, offset: int):
        now = datetime.now()
        return self.repo.list_upcoming(now=now, limit=limit, offset=offset)
