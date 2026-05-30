import os
import threading
from typing import Any, Optional

import yaml


class AppConfig:
    _instance: Optional["AppConfig"] = None
    _lock = threading.Lock()

    def __init__(self):
        self.db_host: str = "localhost"
        self.db_port: int = 3306
        self.db_user: str = "template_user"
        self.db_password: str = "template_pass"
        self.db_name: str = "template_db"
        self.db_charset: str = "utf8mb4"

        self.openai_api_key: str = ""
        self.openai_base_url: str = ""
        self.openai_model: str = "gpt-4o-mini"

        self.debug: bool = False
        self.app_name: str = "project-template"
        self.heartbeat_message: str = "template alive"
        self.config_source: str = "defaults"

    @classmethod
    def get_instance(cls) -> "AppConfig":
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = cls()
        return cls._instance

    def load_from_yaml(self, yaml_str: str):
        data = yaml.safe_load(yaml_str)
        if not data:
            return
        self._apply_mapping(data)
        self.config_source = "nacos"

    def load_from_env(self):
        self.db_host = os.getenv("DB_HOST", self.db_host)
        self.db_port = int(os.getenv("DB_PORT", str(self.db_port)))
        self.db_user = os.getenv("DB_USER", self.db_user)
        self.db_password = os.getenv("DB_PASSWORD", self.db_password)
        self.db_name = os.getenv("DB_NAME", self.db_name)
        self.db_charset = os.getenv("DB_CHARSET", self.db_charset)

        self.openai_api_key = os.getenv("OPENAI_API_KEY", self.openai_api_key)
        self.openai_base_url = os.getenv("OPENAI_BASE_URL", self.openai_base_url)
        self.openai_model = os.getenv("OPENAI_MODEL", self.openai_model)

        self.debug = os.getenv("APP_DEBUG", "").lower() == "true"
        self.config_source = "env"

    def _apply_mapping(self, data: dict[str, Any]):
        db = data.get("database", {})
        self.db_host = db.get("host", self.db_host)
        self.db_port = int(db.get("port", self.db_port))
        self.db_user = db.get("user", self.db_user)
        self.db_password = db.get("password", self.db_password)
        self.db_name = db.get("name", self.db_name)
        self.db_charset = db.get("charset", self.db_charset)

        openai = data.get("openai", {})
        self.openai_api_key = openai.get("api_key", self.openai_api_key)
        self.openai_base_url = openai.get("base_url", self.openai_base_url)
        self.openai_model = openai.get("model", self.openai_model)

        app = data.get("app", {})
        self.debug = app.get("debug", self.debug)
        self.app_name = app.get("name", self.app_name)
        self.heartbeat_message = app.get("heartbeat_message", self.heartbeat_message)

    def to_dict(self) -> dict[str, Any]:
        return {
            "database": {
                "host": self.db_host,
                "port": self.db_port,
                "user": self.db_user,
                "password": self.db_password,
                "name": self.db_name,
                "charset": self.db_charset,
            },
            "openai": {
                "api_key": self.openai_api_key,
                "base_url": self.openai_base_url,
                "model": self.openai_model,
            },
            "app": {
                "debug": self.debug,
                "name": self.app_name,
                "heartbeat_message": self.heartbeat_message,
            },
        }

    def merge_update(self, payload: dict[str, Any]):
        current = self.to_dict()
        for key, value in payload.items():
            if isinstance(value, dict) and isinstance(current.get(key), dict):
                current[key].update(value)
            else:
                current[key] = value
        self._apply_mapping(current)

    def to_yaml(self) -> str:
        return yaml.safe_dump(self.to_dict(), sort_keys=False, allow_unicode=True)

    @property
    def database_url(self) -> str:
        return (
            f"mysql+pymysql://{self.db_user}:{self.db_password}"
            f"@{self.db_host}:{self.db_port}/{self.db_name}"
            f"?charset={self.db_charset}"
        )


def get_config() -> AppConfig:
    return AppConfig.get_instance()
