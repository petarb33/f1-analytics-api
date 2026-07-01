from fastapi import APIRouter, Depends
from app.schemas.session import SessionQueryParameters

router = APIRouter()


@router.get("/overtakes")
def get_overtakes_graph(params: SessionQueryParameters = Depends()):
    pass
