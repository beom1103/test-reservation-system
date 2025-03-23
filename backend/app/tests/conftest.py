from collections.abc import Generator

import pytest
from sqlmodel import Session

from app.core.db import engine, init_db


@pytest.fixture(scope="session", autouse=True)
def session() -> Generator[Session, None, None]:
    with Session(engine) as session:
        init_db(session)
        yield session
