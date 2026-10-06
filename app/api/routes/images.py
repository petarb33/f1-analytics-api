from fastapi import APIRouter, HTTPException, Response
from app.models.image import get_image_by_id, get_latest_image

router = APIRouter()


@router.get("/{image_id}")
def get_image_route(image_id: int):
    img = get_image_by_id(image_id)
    if not img:
        raise HTTPException(status_code=404, detail="Image not found")
    return Response(content=img["data"], media_type=img["mime_type"])


@router.get("")
def get_latest_image_route():
    img = get_latest_image()
    if not img:
        raise HTTPException(status_code=404, detail="No images found")
    return Response(content=img["data"], media_type=img["mime_type"])
