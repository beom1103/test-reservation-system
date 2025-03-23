from fastapi import APIRouter, Depends, Query

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
    summary="[User] 시험 일정 목록 조회",
    description="""
고객이 예약 가능한 시험 일정을 조회합니다.

- 시험 시작 시간이 현재 이후인 일정만 조회됩니다.
- 각 일정에 대해 `isApplied` 값으로 예약 여부를 함께 제공합니다.
- 페이징 방식으로 `limit`, `offset` 사용
""",
)
def paginate_tryouts(
    session: SessionDep,
    current_user: User = Depends(get_current_user),
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
) -> PaginatedResponse[TryoutPublic]:
    return TryoutService(session).paginate_upcoming_tryouts(
        limit=limit, offset=offset, user_id=current_user.id
    )


@router.get(
    "/{tryout_id}",
    response_model=TryoutPublic,
    summary="[User] 시험 일정 상세 조회",
    description="""
시험 일정 정보를 조회합니다.

- 로그인한 사용자가 해당 일정에 예약했는지 여부도 함께 반환됩니다.
""",
)
def get_tryout_by_id(
    tryout_id: int, session: SessionDep, current_user: CurrentUser
) -> TryoutPublic:
    return TryoutService(session).get_tryout_by_id(tryout_id, current_user.id)


@router.post(
    "/{tryout_id}/reserve",
    response_model=Reservation,
    summary="[User 전용] 시험 일정 예약 신청",
    description="""
고객이 특정 시험 일정에 예약을 신청합니다.

- 어드민은 예약 신청이 불가능합니다.
- 예약 신청은 시험 시작 3일 전까지 가능하며, 동시간대 확정 인원 5만명을 초과할 수 없습니다.
- 하나의 시험에 대해 중복 예약은 불가하며, 기존 삭제된 예약은 재사용됩니다.
""",
)
def reserve_tryout(
    session: SessionDep,
    tryout_id: int,
    reserved_seats: int = Query(..., gt=0, le=50000, description="신청 인원 수"),
    current_user: User = Depends(get_current_user),
) -> Reservation:
    return TryoutService(session).reserve_tryout(
        tryout_id=tryout_id,
        user_id=current_user.id,
        reserved_seats=reserved_seats,
    )
