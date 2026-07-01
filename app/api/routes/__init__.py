from fastapi import APIRouter
from app.api.routes import routes, auth, analysis

api_router = APIRouter()
api_router.include_router(routes.router)
api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(analysis.router, prefix="/analysis", tags=["analysis"])
