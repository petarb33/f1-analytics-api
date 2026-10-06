from fastapi import APIRouter, Depends
from app.api.routes import season, auth, analysis, images
from app.core.dependencies import get_current_user

api_router = APIRouter()
api_router.include_router(season.router, prefix="/season", tags=["season"])
api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(
    analysis.router,
    prefix="/analysis/{year}/{round_number}/{session}",
    tags=["analysis"],
    dependencies=[Depends(get_current_user)],
)
api_router.include_router(images.router, prefix="/images", tags=["images"])
