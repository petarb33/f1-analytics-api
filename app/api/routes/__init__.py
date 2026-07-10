from fastapi import APIRouter
from app.api.routes import season, auth, analysis

api_router = APIRouter()
api_router.include_router(season.router, prefix="/season", tags=["season"])
api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(
    analysis.router,
    prefix="/analysis/{year}/{round_number}/{session}",
    tags=["analysis"],
)
