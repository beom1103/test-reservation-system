from fastapi import APIRouter, Depends, HTTPException, Query
from starlette.status import HTTP_400_BAD_REQUEST

from app.dependencies import CurrentUser, SessionDep, get_current_user
from app.models.common import PaginatedResponse
from app.models.reservations import Reservation
from app.models.tryouts import TryoutPublic
from app.models.users import User
from app.services.tryouts import TryoutService

router = APIRouter(prefix="/tryouts", tags=["tryouts"])


@router.get(
    "",
    response_model=PaginatedResponse[TryoutPublic],
    summary="시험 일정 조회",
)
def paginate_tryouts(
    session: SessionDep,
    current_user: User = Depends(get_current_user),
    limit: int = Query(20, ge=1),
    offset: int = Query(0, ge=0),
) -> PaginatedResponse[TryoutPublic]:
    try:
        return TryoutService(session).paginate_upcoming_tryouts(
            limit=limit, offset=offset, user_id=current_user.id
        )
    except ValueError as e:
        raise HTTPException(status_code=HTTP_400_BAD_REQUEST, detail=str(e))


@router.get(
    "/{tryout_id}",
    response_model=TryoutPublic,
    summary="시험 정보 조회",
)
def get_tryout_by_id(
    tryout_id: int, session: SessionDep, current_user: CurrentUser
) -> TryoutPublic:
    return TryoutService(session).get_tryout_by_id(tryout_id, current_user.id)


@router.post("/{tryout_id}/reserve", response_model=Reservation, summary="시험 신청")
def reserve_tryout(
    session: SessionDep,
    tryout_id: int,
    reserved_seats: int = Query(..., gt=0, le=50000),
    current_user: User = Depends(get_current_user),
) -> Reservation:
    if current_user.is_superuser:
        raise HTTPException(status_code=403, detail="Admin은 시험 신청이 불가합니다.")

    return TryoutService(session).reserve_tryout(
        tryout_id=tryout_id,
        user_id=current_user.id,
        reserved_seats=reserved_seats,
    )
