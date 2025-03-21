from fastapi import APIRouter, Depends, HTTPException, Query
from starlette.status import HTTP_400_BAD_REQUEST

from app.dependencies import SessionDep, get_current_user
from app.models.tryouts import TryoutPublic
from app.models.users import User
from app.services.tryouts import TryoutService

router = APIRouter(prefix="/tryouts", tags=["tryouts"])


@router.get(
    "",
    response_model=list[TryoutPublic],
    summary="시험 일정 조회",
)
def get_tryouts(
    session: SessionDep,
    current_user: User = Depends(get_current_user),
    limit: int = Query(20, ge=1),
    offset: int = Query(0, ge=0),
):
    try:
        return TryoutService(session).get_upcoming_tryouts(
            limit=limit, offset=offset, user_id=current_user.id
        )
    except ValueError as e:
        raise HTTPException(status_code=HTTP_400_BAD_REQUEST, detail=str(e))
