
import json
import os


class ConfigManager:
    def __init__(self, config_file="config.json"):
        self.config_file = config_file
        self.defaults = {"watched_folders": [], "theme": "light"}
        self.settings = self.load_config()
        self._last_mtime = self._get_mtime()

    def _get_mtime(self):
        if os.path.exists(self.config_file):
            return os.path.getmtime(self.config_file)
        return None


    def load_config(self):
        mtime = self._get_mtime()
        if mtime and mtime == getattr(self, '_last_mtime', None):
            return self.settings
        if os.path.exists(self.config_file):
            with open(self.config_file, 'r') as f:
                self._last_mtime = mtime
                return {**self.defaults, **json.load(f)}
        return self.defaults.copy()


    def save_config(self):
        with open(self.config_file, 'w') as f:
            json.dump(self.settings, f, indent=4)
        self._last_mtime = self._get_mtime()

    def reset_to_defaults(self):
        """Reset configuration to default values and save."""
        self.settings = self.defaults.copy()
        self.save_config()

    def update_config(self, key, value):
        """Update a single config key with type validation."""
        if key not in self.defaults:
            raise KeyError(f"Unknown config key: {key}")
        if not isinstance(value, type(self.defaults[key])):
            raise TypeError(f"Value for {key} must be of type {type(self.defaults[key]).__name__}")
        self.settings[key] = value
        self.save_config()