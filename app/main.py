import traceback

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder
from pydantic import ValidationError
from app.api.routes import api_router
from app.core.logging import configure_logging, logger
from app.core.exceptions import AnalysisDataError

configure_logging()

app = FastAPI()


@app.exception_handler(ValidationError)
async def pydantic_validation_exception_handler(request: Request, exc: ValidationError):
    return JSONResponse(
        status_code=422, content=jsonable_encoder({"detail": exc.errors()})
    )


@app.exception_handler(AnalysisDataError)
async def analysis_data_error_handler(request: Request, exc: AnalysisDataError):
    return JSONResponse(status_code=404, content={"detail": str(exc)})


@app.exception_handler(Exception)
async def unhandled_exception_handler(request: Request, exc: Exception):
    logger.error(
        "unhandled_exception",
        path=request.url.path,
        error=str(exc),
        traceback="".join(
            traceback.format_exception(type(exc), exc, exc.__traceback__)
        ),
    )
    return JSONResponse(status_code=500, content={"detail": "Internal server error"})


app.include_router(api_router, prefix="/api/v1")
