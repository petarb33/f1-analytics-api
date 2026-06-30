from fastapi import APIRouter
from app.api.routes import routes, auth

api_router = APIRouter()
api_router.include_router(routes.router)
api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
