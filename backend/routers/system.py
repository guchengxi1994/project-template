from datetime import datetime

from fastapi import APIRouter, HTTPException

from app_config import get_config
from database import record_heartbeat
from logging_config import get_logger
from nacos_config import publish_config
from schemas.config import ConfigUpdateRequest

logger = get_logger()
router = APIRouter(prefix="/api/system", tags=["system"])


@router.get("/config")
async def get_system_config():
    config = get_config()
    logger.info("read config, source={}", config.config_source)
    return {
        "nacos_enabled": config.config_source == "nacos",
        "config_source": config.config_source,
        "data": config.to_dict(),
    }


@router.put("/config")
async def update_system_config(request: ConfigUpdateRequest):
    config = get_config()
    payload = request.model_dump(exclude_none=True)
    if not payload:
        logger.warning("reject empty config update payload")
        raise HTTPException(status_code=400, detail="empty config payload")

    logger.info("update config keys={}", ",".join(payload.keys()))
    config.merge_update(payload)

    published = await publish_config(config.to_yaml())
    if published:
        config.config_source = "nacos"
        logger.info("config published to nacos")
    elif config.config_source == "nacos":
        logger.error("failed to publish config to nacos")
        raise HTTPException(status_code=502, detail="failed to publish config to nacos")
    else:
        logger.warning("nacos unavailable, config only updated in memory")

    return {
        "success": True,
        "updated_at": datetime.now().isoformat(),
        "config_source": config.config_source,
        "data": config.to_dict(),
    }


@router.post("/heartbeat")
async def heartbeat():
    config = get_config()
    record_heartbeat("api")
    logger.info("heartbeat received")
    return {
        "status": "ok",
        "service": config.app_name,
        "message": config.heartbeat_message,
        "timestamp": datetime.now().isoformat(),
    }

