import json
import os
from typing import Any, Dict

class ConfigManager:
    _instance = None
    DEFAULT_CONFIG = {
        "language": "en",
        "time_update": False,
        "share_data": True
    }

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(ConfigManager, cls).__new__(cls)
            cls._instance._config = {}
            cls._instance._config_file = os.path.join("_internal", "config.json")
            cls._instance._load_config()
        return cls._instance

    def _load_config(self) -> None:
        """Load configuration from JSON file or create default if not exists."""
        try:
            if os.path.exists(self._config_file):
                with open(self._config_file, 'r', encoding='utf-8') as f:
                    self._config = json.load(f)
            else:
                self._config = self.DEFAULT_CONFIG.copy()
                self._save_config()
        except Exception as e:
            print(f"Error loading config: {e}")
            self._config = self.DEFAULT_CONFIG.copy()

    def _save_config(self) -> None:
        """Save current configuration to JSON file."""
        try:
            os.makedirs(os.path.dirname(self._config_file), exist_ok=True)
            with open(self._config_file, 'w', encoding='utf-8') as f:
                json.dump(self._config, f, indent=4)
        except Exception as e:
            print(f"Error saving config: {e}")

    def get(self, key: str, default: Any = None) -> Any:
        """Get a configuration value."""
        return self._config.get(key, default)

    def set(self, key: str, value: Any) -> None:
        """Set a configuration value and save to file."""
        self._config[key] = value
        self._save_config()

    def update(self, config_dict: Dict[str, Any]) -> None:
        """Update multiple configuration values at once."""
        self._config.update(config_dict)
        self._save_config()

    def get_all(self) -> Dict[str, Any]:
        """Get all configuration values."""
        return self._config.copy()
