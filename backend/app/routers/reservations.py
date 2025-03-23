from typing import Annotated

from fastapi import APIRouter, Depends, Query

from app.dependencies import SessionDep, get_current_active_superuser, get_current_user
from app.models.common import PaginatedResponse
from app.models.reservations import Reservation, ReservationUpdateRequest
from app.models.users import User
from app.services.reservations import ReservationService

router = APIRouter(prefix="/reservations", tags=["reservations"])


@router.get(
    "",
    summary="[User/Admin] 예약 목록 조회",
    description="""
- 일반 사용자는 본인의 예약만 확인할 수 있습니다.
- 어드민은 전체 예약 목록을 조회할 수 있습니다.
- `limit`, `offset`을 통해 페이지네이션이 가능합니다.
""",
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


@router.get(
    "/{reservation_id}",
    summary="[User/Admin] 예약 상세 조회",
    description="""
- 본인의 예약이거나, 어드민인 경우 해당 예약 상세 정보를 조회할 수 있습니다.
""",
    response_model=Reservation,
)
def get_reservation_by_id(
    reservation_id: int,
    session: SessionDep,
    current_user: User = Depends(get_current_user),
) -> Reservation:
    return ReservationService(session).get_reservation_by_id(
        reservation_id=reservation_id,
        current_user=current_user,
    )


@router.post(
    "/{reservation_id}/confirm",
    response_model=Reservation,
    summary="[Admin 전용] 예약 확정 처리",
    description="""
- 어드민 전용 기능입니다.
- 고객이 신청한 예약을 확정합니다.
- 이미 확정된 예약이거나, 시험 시작 시간이 지난 경우 확정할 수 없습니다.
""",
    dependencies=[Depends(get_current_active_superuser)],
)
def confirm_reservation(
    reservation_id: int,
    session: SessionDep,
) -> Reservation:
    return ReservationService(session).confirm_reservation(reservation_id)


@router.delete(
    "/{reservation_id}/delete",
    response_model=Reservation,
    summary="[User/Admin] 예약 삭제",
    description="""
- 고객은 본인의 예약 중 '확정되지 않은' 예약만 삭제할 수 있습니다.
- 어드민은 모든 예약을 삭제할 수 있습니다.
- 시험 시작 이후에는 삭제가 제한됩니다.
""",
)
def reject_reservation(
    reservation_id: int,
    session: SessionDep,
    current_user: User = Depends(get_current_user),
) -> Reservation:
    return ReservationService(session).delete_reservation(
        reservation_id, current_user=current_user
    )


@router.patch(
    "/{reservation_id}",
    response_model=Reservation,
    summary="[User/Admin] 예약 수정",
    description="""
- 고객은 본인의 예약 중 '확정되지 않은' 경우에만 수정할 수 있습니다.
- 어드민은 모든 예약을 수정할 수 있습니다.
- 시험 시작 이후에는 예약 수정이 불가능합니다.
""",
)
def update_reservation(
    reservation_id: int,
    update_data: ReservationUpdateRequest,
    session: SessionDep,
    current_user: User = Depends(get_current_user),
) -> Reservation:
    return ReservationService(session).update_reservation(
        reservation_id=reservation_id,
        update_data=update_data,
        user=current_user,
    )
