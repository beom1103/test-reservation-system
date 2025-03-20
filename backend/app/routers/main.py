from fastapi import APIRouter

from app.routers import utils

api_router = APIRouter()
api_router.include_router(utils.router)
