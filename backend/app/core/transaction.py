from collections.abc import Callable
from typing import TypeVar

from sqlmodel import Session

T = TypeVar("T")


class TransactionHelper:
    def __init__(self, session: Session):
        self.session = session

    def run(self, operation: Callable[[], T]) -> T:
        if self.session.in_transaction():
            return operation()
        with self.session.begin():
            return operation()
