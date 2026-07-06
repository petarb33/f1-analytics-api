from fastapi import APIRouter, Depends, Response
from app.schemas.session import SessionQueryParameters
from app.services.analyze import run_overtakes

router = APIRouter()


@router.get("/overtakes")
def get_overtakes_graph(params: SessionQueryParameters = Depends()):
    image_bytes = run_overtakes(params.year, params.round_number, params.session)
    return Response(content=image_bytes, media_type="image/png")
