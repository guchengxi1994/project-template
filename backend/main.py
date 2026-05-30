from contextlib import asynccontextmanager
from datetime import datetime
from time import perf_counter
from uuid import uuid4

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware

from app_config import get_config
from database import init_db, record_heartbeat
from logging_config import get_logger, setup_logging
from nacos_config import close_nacos_config, init_nacos_config
from routers.system import router as system_router

setup_logging()
logger = get_logger()


@asynccontextmanager
async def lifespan(app: FastAPI):
    config = get_config()
    logger.info("application starting")

    nacos_ok = await init_nacos_config()
    if not nacos_ok:
        config.load_from_env()
        logger.warning("nacos unavailable, fallback to env")
    else:
        logger.info("nacos config loaded successfully")

    init_db()
    logger.info("database initialized")
    record_heartbeat("startup")
    logger.info("startup heartbeat recorded")

    yield

    logger.info("application shutting down")
    await close_nacos_config()


app = FastAPI(
    title="Project Template API",
    description="Minimal FastAPI template with Nacos-backed config",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.middleware("http")
async def request_logging_middleware(request: Request, call_next):
    request_id = str(uuid4())[:8]
    started = perf_counter()
    logger.info("request start id={} method={} path={}", request_id, request.method, request.url.path)
    response = await call_next(request)
    duration_ms = (perf_counter() - started) * 1000
    logger.info(
        "request end id={} method={} path={} status={} duration_ms={:.2f}",
        request_id,
        request.method,
        request.url.path,
        response.status_code,
        duration_ms,
    )
    return response


app.include_router(system_router)


@app.get("/")
async def root():
    config = get_config()
    logger.info("root endpoint hit")
    return {
        "message": f"{config.app_name} is running",
    }


@app.get("/health")
async def health_check():
    config = get_config()
    logger.debug("health check ok")
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "service": config.app_name,
        "message": config.heartbeat_message,
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)
