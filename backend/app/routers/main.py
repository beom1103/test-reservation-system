from fastapi import APIRouter

from app.routers import tryouts, utils

api_router = APIRouter()

api_router.include_router(utils.router)
api_router.include_router(tryouts.router)
