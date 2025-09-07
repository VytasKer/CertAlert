# backend/app/admin_settings.py

from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import Dict, Any, Optional
import logging
import os
import json
from app.database import SessionLocal
from app.models import TrafficLog, AdminSetting

logger = logging.getLogger("admin_settings")

class AdminSettings:
    """Manage admin configurable settings with database persistence"""
    
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
    
    def __init__(self, db: Session = None):
        self.db = db or SessionLocal()
        self._should_close_db = db is None
        self._initialize_defaults()
    
    def __del__(self):
        """Close database session if we created it"""
        if hasattr(self, '_should_close_db') and self._should_close_db and hasattr(self, 'db'):
            self.db.close()
    
    def _initialize_defaults(self):
        """Initialize default settings in database if they don't exist"""
        for key, config in self.DEFAULT_SETTINGS.items():
            existing = self.db.query(AdminSetting).filter(AdminSetting.key == key).first()
            if not existing:
                new_setting = AdminSetting(
                    key=key,
                    value=str(config["value"])
                )
                self.db.add(new_setting)
        self.db.commit()
    
    def get_setting(self, key: str) -> Dict[str, Any]:
        """Get a setting with its metadata"""
        if key not in self.DEFAULT_SETTINGS:
            raise ValueError(f"Unknown setting: {key}")
        
        config = self.DEFAULT_SETTINGS[key]
        
        # Get value from database
        db_setting = self.db.query(AdminSetting).filter(AdminSetting.key == key).first()
        current_value = config["value"]  # default
        
        if db_setting:
            # Convert string value back to appropriate type
            if config["type"] == "integer":
                try:
                    current_value = int(db_setting.value)
                except (ValueError, TypeError):
                    current_value = config["value"]  # fallback to default
            else:
                current_value = db_setting.value
        
        return {
            "key": key,
            "current_value": current_value,
            "saved": True,  # Values in DB are always considered saved
            **config
        }
    
    def get_all_settings(self) -> Dict[str, Dict[str, Any]]:
        """Get all settings with their metadata"""
        settings = {}
        for key in self.DEFAULT_SETTINGS:
            settings[key] = self.get_setting(key)
        return settings
    
    def update_setting(self, key: str, value: Any):
        """Update a setting value in database"""
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
        
        # Update or create setting in database
        db_setting = self.db.query(AdminSetting).filter(AdminSetting.key == key).first()
        if db_setting:
            db_setting.value = str(value)
            db_setting.updated_at = func.now()
        else:
            db_setting = AdminSetting(key=key, value=str(value))
            self.db.add(db_setting)
        
        self.db.commit()
        
        # Apply the setting to the system immediately
        self._apply_setting(key, value)
        
        # Return the full setting object
        return {
            "key": key,
            "current_value": value,
            "saved": True,
            **config
        }
    
    def save_setting(self, key: str):
        """For backward compatibility - settings are now saved immediately in update_setting"""
        return self.get_setting(key)
    
    def reset_setting(self, key: str):
        """Reset a setting to its default value"""
        if key not in self.DEFAULT_SETTINGS:
            return {"error": f"Setting '{key}' not found"}
        
        default_value = self.DEFAULT_SETTINGS[key]["value"]
        
        # Update in database
        db_setting = self.db.query(AdminSetting).filter(AdminSetting.key == key).first()
        if db_setting:
            db_setting.value = str(default_value)
            db_setting.updated_at = func.now()
        else:
            db_setting = AdminSetting(key=key, value=str(default_value))
            self.db.add(db_setting)
        
        self.db.commit()
        
        # Apply the default setting
        self._apply_setting(key, default_value)
        
        # Return the full setting object
        return {
            "key": key,
            "current_value": default_value,
            "saved": True,
            **self.DEFAULT_SETTINGS[key]
        }
    
    def _apply_setting(self, key: str, value: Any):
        """Apply a setting to the running system"""
        if key == "traffic_log_retention_days":
            try:
                from traffic_config import traffic_config
                traffic_config.RETENTION_DAYS = int(value)
                logger.info(f"Updated traffic log retention to {value} days")
            except ImportError:
                logger.warning("traffic_config not available, setting stored but not applied to config")
        
        return True

# Global settings instance
admin_settings = AdminSettings()
