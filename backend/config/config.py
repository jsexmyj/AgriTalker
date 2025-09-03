import yaml
from typing import Any
from pathlib import Path


class ConfigManager:
    _config = None  # 私有类变量，避免重复加载

    @classmethod
    def load_config(cls, path: str = "backend\config\config.yaml"):
        if cls._config is None:
            config_path = Path(path)
            with config_path.open("r", encoding="utf-8") as f:
                cls._config = yaml.safe_load(f)

    @classmethod
    def get(cls, key: str, default: Any = None) -> Any:
        # 支持 key.subkey 的访问方式
        if cls._config is None:
            raise ValueError(
                "Config not loaded. Call `ConfigManager.load_config()` first."
            )

        keys = key.split(".")
        value = cls._config
        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return default
        return value
