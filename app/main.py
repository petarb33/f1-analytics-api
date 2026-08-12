from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder
from pydantic import ValidationError
from app.api.routes import api_router

app = FastAPI()


@app.exception_handler(ValidationError)
async def pydantic_validation_exception_handler(request: Request, exc: ValidationError):
    return JSONResponse(
        status_code=422, content=jsonable_encoder({"detail": exc.errors()})
    )


app.include_router(api_router, prefix="/api/v1")
