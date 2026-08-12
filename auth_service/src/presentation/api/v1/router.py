from fastapi import APIRouter

from src.presentation.api.v1.routers.auth import router as auth_router

api_v1_router = APIRouter(prefix="/api/v1")
api_v1_router.include_router(auth_router)
