from fastapi import APIRouter

from app.routers import reservations, tryouts, utils

api_router = APIRouter()

api_router.include_router(utils.router)
api_router.include_router(tryouts.router)
api_router.include_router(reservations.router)
