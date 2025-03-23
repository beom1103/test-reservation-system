from typing import Annotated

from fastapi import APIRouter, Depends, Query

from app.dependencies import SessionDep, get_current_user
from app.models.common import PaginatedResponse
from app.models.reservations import Reservation
from app.models.users import User
from app.services.reservations import ReservationService

router = APIRouter(prefix="/reservations", tags=["reservations"])


@router.get(
    "",
    summary="예약 목록 조회",
    description="일반 사용자는 자신의 예약 목록을, 어드민은 모든 예약 목록을 조회할 수 있습니다.",
    response_model=PaginatedResponse[Reservation],
)
def paginate_reservations(
    session: SessionDep,
    current_user: Annotated[User, Depends(get_current_user)],
    limit: Annotated[int, Query(ge=1, le=1000)] = 10,
    offset: Annotated[int, Query(ge=0)] = 0,
) -> PaginatedResponse[Reservation]:
    return ReservationService(session).paginate_reservations(
        user=current_user,
        limit=limit,
        offset=offset,
    )
