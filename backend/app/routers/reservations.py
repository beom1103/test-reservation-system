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


@router.get(
    "/{reservation_id}",
    summary="예약 단건 조회",
    description="본인 예약 또는 어드민은 단건 예약 조회 가능",
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
    summary="예약 확정",
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
    summary="예약 삭제",
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
    summary="예약 수정",
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
