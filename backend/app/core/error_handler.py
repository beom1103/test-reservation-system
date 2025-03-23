from fastapi import Request
from fastapi.responses import JSONResponse

from app.core.exceptions import (
    AlreadyReservedError,
    AuthorizationError,
    InvalidReservationPeriodError,
    ReservationNotFoundError,
    TryoutFullError,
    TryoutNotFoundError,
)


def register_error_handlers(app):
    @app.exception_handler(TryoutNotFoundError)
    async def tryout_not_found_handler(_: Request, __: TryoutNotFoundError):
        return JSONResponse(
            status_code=404, content={"detail": "시험을 찾을 수 없습니다."}
        )

    @app.exception_handler(InvalidReservationPeriodError)
    async def invalid_period_handler(_: Request, __: InvalidReservationPeriodError):
        return JSONResponse(
            status_code=400, content={"detail": "신청 기간이 아닙니다."}
        )

    @app.exception_handler(AlreadyReservedError)
    async def already_reserved_handler(_: Request, exc: AlreadyReservedError):
        return JSONResponse(
            status_code=400,
            content={"detail": str(exc) or "이미 신청된 시험입니다."},
        )

    @app.exception_handler(TryoutFullError)
    async def tryout_full_handler(_: Request, __: TryoutFullError):
        return JSONResponse(
            status_code=400, content={"detail": "정원이 가득 찼습니다."}
        )

    @app.exception_handler(ReservationNotFoundError)
    async def reservation_not_found_handler(_: Request, __: ReservationNotFoundError):
        return JSONResponse(
            status_code=404, content={"detail": "예약을 찾을 수 없습니다."}
        )

    @app.exception_handler(AuthorizationError)
    async def not_authorized_handler(_: Request, __: AuthorizationError):
        return JSONResponse(
            status_code=403, content={"detail": "접근 권한이 없습니다."}
        )
