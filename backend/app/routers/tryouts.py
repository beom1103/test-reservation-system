from fastapi import APIRouter, Depends, HTTPException, Query
from starlette.status import HTTP_400_BAD_REQUEST

from app.dependencies import SessionDep, get_current_user
from app.models.tryouts import TryoutPublic
from app.services.tryouts import TryoutService

router = APIRouter(prefix="/tryouts", tags=["tryouts"])


@router.get(
    "",
    dependencies=[Depends(get_current_user)],
    response_model=list[TryoutPublic],
    summary="시험 일정 조회",
    description="""
- 이미 종료된 시험은 제외
- 시작 시간 기준 오름차순 정렬
- pagination 지원 (limit, offset)
""",
)
def get_tryouts(
    session: SessionDep,
    limit: int = Query(20, ge=1),
    offset: int = Query(0, ge=0),
):
    try:
        return TryoutService(session).get_upcoming_tryouts(limit=limit, offset=offset)
    except ValueError as e:
        raise HTTPException(status_code=HTTP_400_BAD_REQUEST, detail=str(e))
