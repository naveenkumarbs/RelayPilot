import logging
from contextlib import asynccontextmanager
from time import perf_counter
from uuid import uuid4

from fastapi import FastAPI, Request

from app.core.logging_config import configure_logging
from app.api.router import api_router
from app.core.config import get_settings
from app.db.session import engine 

settings = get_settings()
configure_logging(settings.log_level)

logger = logging.getLogger("relaypilot.api")

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("event=application_started environment=%s ", settings.environment)
    try:
        yield
    finally:
        engine.dispose()
        logger.info("event=application_stopped")


app = FastAPI(
    title=settings.app_name,
    description="Multi-tenant AI customer support platform.",
    version=settings.app_version,
    lifespan=lifespan,
)

@app.middleware("http")
async def log_requests(request: Request, call_next):
    request_id = uuid4().hex
    request.state.request_id = request_id

    started_at = perf_counter()

    try:
        response = await call_next(request)
    except Exception:
        duration_ms = (perf_counter() - started_at) * 1000
        logger.exception(
            "event=request_failed request_id=%s method=%s "
            "duration_ms=%.2f",
            request_id,
            request.method,
            duration_ms
        )
        raise
    
    duration_ms = (perf_counter() - started_at) * 1000

    # Prefer route templates such as /tickets/{ticket_id}
    # Avoid loggin raw paths, wich can contain customer identifiers.
    route = request.scope.get("route")
    route_name = getattr(route, "path", "<unmatched>")

    log_level = (
        logging.ERROR
        if response.status_code >=500
        else logging.WARNING
        if response.status_code >=400
        else logging.INFO
    )

    logger.log(
        log_level,
        "event=request_completed request_id=%s method=%s "
        "route=%s status_code=%s duration_ms=%.2f",
        request_id,
        request.method,
        route_name,
        response.status_code,
        duration_ms,
    )

    response.headers["X-Request-ID"] = request_id

    return response


app.include_router(api_router)