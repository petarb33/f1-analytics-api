from fastapi import APIRouter
from app.services.fetch import list_seasons, list_races

router = APIRouter()


@router.get("/")
def root():
    return {"message": "Hello World"}


@router.get("/seasons")
def seasons():
    return {"seasons": list_seasons()}


@router.get("/seasons/{year}/races")
def season(year: int):
    return {f"races for season {year}": list_races(year)}
