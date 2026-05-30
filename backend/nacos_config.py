import asyncio
import logging
import os
from urllib import parse, request
from typing import Any

from app_config import AppConfig

logger = logging.getLogger(__name__)

NACOS_SERVER_ADDR = os.getenv("NACOS_SERVER_ADDR", "127.0.0.1:8848")
NACOS_DATA_ID = os.getenv("NACOS_DATA_ID", "TEMPLATE_CONFIG")
NACOS_GROUP = os.getenv("NACOS_GROUP", "TEMPLATE")

_nacos_service = None


async def init_nacos_config() -> bool:
    global _nacos_service

    try:
        from v2.nacos import ClientConfigBuilder, ConfigParam, GRPCConfig, NacosConfigService
    except ImportError:
        logger.warning("nacos sdk v2 not installed")
        return False

    try:
        client_config = (
            ClientConfigBuilder()
            .server_address(NACOS_SERVER_ADDR)
            .log_level("INFO")
            .grpc_config(GRPCConfig(grpc_timeout=5000))
            .build()
        )
        _nacos_service = await NacosConfigService.create_config_service(client_config)
        config_param = ConfigParam(data_id=NACOS_DATA_ID, group=NACOS_GROUP)
        yaml_data = await _nacos_service.get_config(config_param)
        if not yaml_data:
            logger.warning("empty nacos config")
            return False

        config = AppConfig.get_instance()
        config.load_from_yaml(yaml_data)
        asyncio.create_task(_watch_config(_nacos_service, config, config_param))
        logger.info("nacos config loaded")
        return True
    except Exception as exc:
        logger.warning("nacos config load failed: %s", exc)
        return False


async def _watch_config(service: Any, config: AppConfig, param: Any):
    async def on_change(tenant: str, data_id: str, group: str, content: str):
        logger.info("nacos config changed: %s/%s", group, data_id)
        config.load_from_yaml(content)

    await service.add_listener(data_id=param.data_id, group=param.group, listener=on_change)


async def publish_config(content: str) -> bool:
    def _publish() -> bool:
        endpoint = f"http://{NACOS_SERVER_ADDR}/nacos/v1/cs/configs"
        payload = parse.urlencode(
            {
                "dataId": NACOS_DATA_ID,
                "group": NACOS_GROUP,
                "type": "yaml",
                "content": content,
            }
        )
        body = payload.encode("utf-8")
        req = request.Request(endpoint, data=body, method="POST")
        with request.urlopen(req, timeout=10) as response:
            result = response.read().decode("utf-8").strip().lower()
            return result == "true"

    try:
        return await asyncio.to_thread(_publish)
    except Exception as exc:
        logger.warning("nacos config publish failed: %s", exc)
        return False


async def close_nacos_config():
    if _nacos_service:
        await _nacos_service.shutdown()
