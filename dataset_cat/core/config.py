"""Configuration management for Dataset Cat.

This module handles loading, saving, and accessing application configuration.
"""

import json
import os
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

# Default configuration values
DEFAULT_CONFIG = {
    "output_dir": str(Path.home() / "dataset-cat" / "output"),
    "temp_dir": str(Path.home() / "dataset-cat" / "temp"),
    "ui": {
        "theme": "default",
        "language": "en",
        "enable_analytics": False,
    },
    "fetcher": {
        "retry_count": 3,
        "timeout": 30,
        "max_parallel_downloads": 5,
        "wait_time": 0.5,  # Wait time between API calls in seconds
    },
    "processing": {
        "default_actions": ["AlignMinSizeAction"],
        "default_params": {
            "AlignMinSizeAction": {"target": 800},
            "AlignMaxSizeAction": {"target": 1024},
            "MinSizeFilterAction": {"size": 256},
        },
        "use_cuda": False,
    },
}


class Config:
    """Configuration manager for Dataset Cat."""

    def __init__(self) -> None:
        """Initialize the configuration manager."""
        self.config_dir = Path.home() / ".dataset-cat"
        self.config_file = self.config_dir / "config.json"
        self._config: Dict[str, Any] = {}
        self._load_config()

    def _load_config(self) -> None:
        """Load configuration from file or create default."""
        try:
            if self.config_file.exists():
                with open(self.config_file, "r", encoding="utf-8") as f:
                    user_config = json.load(f)

                # Merge with defaults to ensure all required keys exist
                self._config = DEFAULT_CONFIG.copy()
                self._update_dict_recursive(self._config, user_config)
            else:
                self._config = DEFAULT_CONFIG.copy()
                self._save_config()
        except Exception as e:
            print(f"Error loading config: {e}")
            self._config = DEFAULT_CONFIG.copy()

    def _save_config(self) -> None:
        """Save configuration to file."""
        try:
            os.makedirs(self.config_dir, exist_ok=True)
            with open(self.config_file, "w", encoding="utf-8") as f:
                json.dump(self._config, f, indent=2)
        except Exception as e:
            print(f"Error saving config: {e}")

    def _update_dict_recursive(self, base_dict: Dict, update_dict: Dict) -> None:
        """Recursively update a dictionary with values from another dictionary.

        Args:
            base_dict: Dictionary to be updated
            update_dict: Dictionary with values to update
        """
        for key, value in update_dict.items():
            if key in base_dict and isinstance(base_dict[key], dict) and isinstance(value, dict):
                self._update_dict_recursive(base_dict[key], value)
            else:
                base_dict[key] = value

    def get(self, key_path: str, default: Any = None) -> Any:
        """Get a configuration value by its key path.

        Args:
            key_path: Dot-separated path to the configuration value
            default: Default value if key doesn't exist

        Returns:
            Configuration value or default
        """
        parts = key_path.split(".")
        current = self._config

        try:
            for part in parts:
                current = current[part]
            return current
        except (KeyError, TypeError):
            return default

    def set(self, key_path: str, value: Any) -> None:
        """Set a configuration value by its key path.

        Args:
            key_path: Dot-separated path to the configuration value
            value: Value to set
        """
        parts = key_path.split(".")
        current = self._config

        # Navigate to the right level
        for i, part in enumerate(parts[:-1]):
            if part not in current:
                current[part] = {}
            current = current[part]

        # Set the value
        current[parts[-1]] = value
        self._save_config()

    def get_output_dir(self) -> str:
        """Get the output directory path.

        Returns:
            Path to the output directory
        """
        path = self.get("output_dir")
        os.makedirs(path, exist_ok=True)
        return path

    def get_temp_dir(self) -> str:
        """Get the temporary directory path.

        Returns:
            Path to the temporary directory
        """
        path = self.get("temp_dir")
        os.makedirs(path, exist_ok=True)
        return path


# Global configuration instance
config = Config()

__all__ = ["config", "Config"]
