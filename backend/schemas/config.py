from typing import Any

from pydantic import BaseModel


class ConfigUpdateRequest(BaseModel):
    database: dict[str, Any] | None = None
    openai: dict[str, Any] | None = None
    app: dict[str, Any] | None = None
