import logging
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.api.v1.router import api_router
from app.core.config import settings
from app.core.errors import AppError
from app.core.rate_limit import limiter
from app.core.responses import ok

logger = logging.getLogger("cabinet")


def _error(
    status_code: int,
    code: str,
    message: str,
    details: list | None = None,
) -> JSONResponse:
    body: dict = {"error": {"code": code, "message": message}}
    if details:
        body["error"]["details"] = details
    return JSONResponse(status_code=status_code, content=body)


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Cabinet API starting in %s mode", settings.environment)
    yield


def create_app() -> FastAPI:
    app = FastAPI(
        title="Cabinet API",
        version="0.1.0",
        description="A curated archive of things worth keeping.",
        docs_url="/api/docs",
        redoc_url=None,
        openapi_url="/api/openapi.json",
        lifespan=lifespan,
    )

    app.state.limiter = limiter
    app.add_middleware(SlowAPIMiddleware)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.allowed_origins_list,
        allow_credentials=True,
        allow_methods=["GET", "POST", "PATCH", "DELETE", "OPTIONS"],
        allow_headers=["*"],
        expose_headers=["Content-Disposition"],
    )
    app.add_middleware(GZipMiddleware, minimum_size=1024)

    app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

    @app.exception_handler(AppError)
    async def handle_app_error(request: Request, exc: AppError) -> JSONResponse:
        return _error(exc.status_code, exc.code, exc.message, exc.details)

    @app.exception_handler(RequestValidationError)
    async def handle_validation_error(
        request: Request, exc: RequestValidationError
    ) -> JSONResponse:
        details = [
            {
                "field": ".".join(str(part) for part in error.get("loc", [])),
                "message": error.get("msg", "Invalid value."),
            }
            for error in exc.errors()
        ]
        return _error(422, "VALIDATION_ERROR", "The request contains invalid values.", details)

    @app.exception_handler(StarletteHTTPException)
    async def handle_http_error(
        request: Request, exc: StarletteHTTPException
    ) -> JSONResponse:
        codes = {
            400: "BAD_REQUEST",
            401: "UNAUTHENTICATED",
            403: "FORBIDDEN",
            404: "NOT_FOUND",
            405: "METHOD_NOT_ALLOWED",
            429: "RATE_LIMITED",
        }
        code = codes.get(exc.status_code, "HTTP_ERROR")
        message = exc.detail if isinstance(exc.detail, str) else "Request could not be completed."
        return _error(exc.status_code, code, message)

    @app.exception_handler(Exception)
    async def handle_unexpected(request: Request, exc: Exception) -> JSONResponse:
        logger.exception("Unhandled error while serving %s", request.url.path)
        return _error(500, "INTERNAL_ERROR", "Something went wrong on our side.")

    app.include_router(api_router, prefix="/api/v1")

    @app.get("/health", tags=["system"])
    async def root_health() -> dict:
        return ok({"status": "ok"})

    @app.get("/", include_in_schema=False)
    async def root() -> dict:
        return ok(
            {
                "name": "Cabinet API",
                "version": "0.1.0",
                "docs": "/api/docs",
            }
        )

    if settings.storage_backend.lower() == "local":
        media_dir = Path(settings.media_path)
        media_dir.mkdir(parents=True, exist_ok=True)
        app.mount("/media", StaticFiles(directory=media_dir), name="media")

    return app


app = create_app()
