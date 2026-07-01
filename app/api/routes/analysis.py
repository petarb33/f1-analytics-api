from fastapi import APIRouter, Depends
from app.schemas.session import SessionQueryParameters
from app.services.analyze import run_overtakes

router = APIRouter()


@router.get("/overtakes")
def get_overtakes_graph(params: SessionQueryParameters = Depends()):
    run_overtakes(params.year, params.round_number, params.session)
