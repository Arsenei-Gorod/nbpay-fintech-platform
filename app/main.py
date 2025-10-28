from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from app.core.config import get_settings
from app.core.logging import setup_logging
from app.core.i18n import set_language, _
from app.api.v1.routers.users import router as users_router
from app.api.v1.routers.auth import router as auth_router
from app.infrastructure.db.session import create_all


def create_app() -> FastAPI:
    settings = get_settings()
    setup_logging(env=settings.ENV)
    set_language(settings.LANG)

    app = FastAPI(
        title=settings.APP_NAME,
        version=settings.VERSION,
        docs_url="/docs" if settings.ENABLE_DOCS else None,
        redoc_url=None,
        servers=[{"url": settings.API_PREFIX}],
    )

    # Initialize DB (if configured)
    create_all()

    # Routers
    app.include_router(users_router, prefix=f"{settings.API_PREFIX}/v1", tags=["users"])
    app.include_router(auth_router, prefix=f"{settings.API_PREFIX}/v1", tags=["auth"])

    # HTTPS-only enforcement (configurable)
    if settings.REQUIRE_HTTPS:

        @app.middleware("http")
        async def enforce_https(request: Request, call_next):  # type: ignore[no-redef]
            if request.url.scheme != "https":
                return JSONResponse({"detail": _("HTTPS required")}, status_code=403)
            return await call_next(request)

    @app.get("/health", tags=["meta"])  # simple healthcheck
    def health() -> dict[str, str]:
        return {"status": "ok"}

    @app.get("/")
    def root() -> dict[str, str]:
        return {"message": f"{settings.APP_NAME} is running"}

    return app


app = create_app()
