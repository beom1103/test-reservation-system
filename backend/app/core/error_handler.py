from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from app.core.exceptions import (
    AlreadyReservedError,
    AuthorizationError,
    BadRequestError,
    InvalidReservationPeriodError,
    NotFoundError,
    ReservationNotFoundError,
    TryoutFullError,
)


def register_error_handlers(app: FastAPI) -> None:
    @app.exception_handler(NotFoundError)
    async def not_found_handler(_: Request, exc: NotFoundError) -> JSONResponse:
        return JSONResponse(
            status_code=404,
            content={"detail": str(exc) or "해당 리소스를 찾을 수 없습니다."},
        )

    @app.exception_handler(InvalidReservationPeriodError)
    async def invalid_period_handler(
        _: Request, __: InvalidReservationPeriodError
    ) -> JSONResponse:
        return JSONResponse(
            status_code=400, content={"detail": "신청 기간이 아닙니다."}
        )

    @app.exception_handler(AlreadyReservedError)
    async def already_reserved_handler(
        _: Request, exc: AlreadyReservedError
    ) -> JSONResponse:
        return JSONResponse(
            status_code=400,
            content={"detail": str(exc) or "이미 신청된 시험입니다."},
        )

    @app.exception_handler(TryoutFullError)
    async def tryout_full_handler(_: Request, exc: TryoutFullError) -> JSONResponse:
        return JSONResponse(
            status_code=400,
            content={"detail": str(exc) or "정원이 가득 찼습니다."},
        )

    @app.exception_handler(ReservationNotFoundError)
    async def reservation_not_found_handler(
        _: Request, __: ReservationNotFoundError
    ) -> JSONResponse:
        return JSONResponse(
            status_code=404, content={"detail": "예약을 찾을 수 없습니다."}
        )

    @app.exception_handler(AuthorizationError)
    async def not_authorized_handler(
        _: Request, exc: AuthorizationError
    ) -> JSONResponse:
        return JSONResponse(
            status_code=403,
            content={"detail": str(exc) or "이미 신청된 시험입니다."},
        )

    @app.exception_handler(BadRequestError)
    async def bad_request_handler(_: Request, exc: BadRequestError) -> JSONResponse:
        return JSONResponse(
            status_code=400,
            content={"detail": str(exc) or "잘못된 요청입니다."},
        )
