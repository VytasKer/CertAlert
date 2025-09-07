# backend/app/admin_settings.py

from sqlalchemy.orm import Session
from typing import Dict, Any, Optional
import logging
import os
from app.database import SessionLocal
from app.models import TrafficLog

logger = logging.getLogger("admin_settings")

class AdminSettings:
    """Manage admin configurable settings"""
    
    # Default settings with their metadata
    DEFAULT_SETTINGS = {
        "traffic_log_retention_days": {
            "value": 30,
            "type": "integer",
            "min": 1,
            "max": 365,
            "description": "Number of days to retain traffic logs in database",
            "requires_restart": False
        }
    }
    
    def __init__(self):
        # For now, store settings in memory
        # In a real implementation, you'd store these in a database table
        self._settings = {}
        self._load_default_settings()
    
    def _load_default_settings(self):
        """Load default settings values"""
        for key, config in self.DEFAULT_SETTINGS.items():
            if key not in self._settings:
                self._settings[key] = {
                    "value": config["value"],
                    "saved": True  # Default values are considered "saved"
                }
    
    def get_setting(self, key: str) -> Optional[Dict[str, Any]]:
        """Get a specific setting with its metadata"""
        if key not in self.DEFAULT_SETTINGS:
            return None
        
        config = self.DEFAULT_SETTINGS[key].copy()
        current = self._settings.get(key, {"value": config["value"], "saved": True})
        
        config.update({
            "current_value": current["value"],
            "saved": current["saved"],
            "key": key
        })
        
        return config
    
    def get_all_settings(self) -> Dict[str, Any]:
        """Get all settings with their metadata"""
        settings = {}
        for key in self.DEFAULT_SETTINGS:
            settings[key] = self.get_setting(key)
        return settings
    
    def update_setting(self, key: str, value: Any):
        """Update a setting value (not saved until save_setting is called)"""
        if key not in self.DEFAULT_SETTINGS:
            return {"error": f"Setting '{key}' not found"}
        
        config = self.DEFAULT_SETTINGS[key]
        
        # Validate the value
        if config["type"] == "integer":
            try:
                value = int(value)
                if "min" in config and value < config["min"]:
                    return {"error": f"Value must be at least {config['min']}"}
                if "max" in config and value > config["max"]:
                    return {"error": f"Value must be at most {config['max']}"}
            except (ValueError, TypeError):
                return {"error": "Value must be a valid integer"}
        
        # Update the setting (but mark as not saved)
        self._settings[key] = {
            "value": value,
            "saved": False
        }
        
        # Return the full setting object
        return {
            "key": key,
            "current_value": value,
            "saved": False,
            **config
        }
    
    def save_setting(self, key: str):
        """Save a setting value and apply it"""
        if key not in self._settings:
            return {"error": f"Setting '{key}' not found"}
        
        # Mark as saved
        self._settings[key]["saved"] = True
        
        # Apply the setting to the system
        if key == "traffic_log_retention_days":
            # Update the traffic config if available
            try:
                from traffic_config import traffic_config
                traffic_config.RETENTION_DAYS = self._settings[key]["value"]
                logger.info(f"Updated traffic log retention to {self._settings[key]['value']} days")
            except ImportError:
                logger.warning("traffic_config not available, setting stored but not applied to config")
        
        # Return the full setting object
        return {
            "key": key,
            "current_value": self._settings[key]["value"],
            "saved": self._settings[key]["saved"],
            **self.DEFAULT_SETTINGS[key]
        }
    
    def reset_setting(self, key: str):
        """Reset a setting to its default value"""
        if key not in self.DEFAULT_SETTINGS:
            return {"error": f"Setting '{key}' not found"}
        
        default_value = self.DEFAULT_SETTINGS[key]["value"]
        self._settings[key] = {
            "value": default_value,
            "saved": True
        }
        
        # Apply the default setting
        if key == "traffic_log_retention_days":
            try:
                from traffic_config import traffic_config
                traffic_config.RETENTION_DAYS = default_value
                logger.info(f"Reset traffic log retention to default: {default_value} days")
            except ImportError:
                logger.warning("traffic_config not available, setting stored but not applied to config")
        
        # Return the full setting object
        return {
            "key": key,
            "current_value": default_value,
            "saved": True,
            **self.DEFAULT_SETTINGS[key]
        }
        
        return True

# Global settings instance
admin_settings = AdminSettings()
