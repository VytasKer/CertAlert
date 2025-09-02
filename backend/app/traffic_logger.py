# backend/app/traffic_logger.py

import json
import hashlib
import asyncio
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, Any, Optional
import logging
import os
from fastapi import Request

from traffic_config import traffic_config

# Configure logging for traffic system
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("traffic_logger")

class TrafficLogger:
    """Handles traffic logging to date-based JSON files"""
    
    def __init__(self):
        self.log_dir = Path(traffic_config.LOG_DIR)
        self.log_dir.mkdir(parents=True, exist_ok=True)
        self._ensure_log_directory()
    
    def _ensure_log_directory(self):
        """Ensure log directory exists"""
        try:
            self.log_dir.mkdir(parents=True, exist_ok=True)
            logger.info(f"Traffic log directory ready: {self.log_dir}")
        except Exception as e:
            logger.error(f"Failed to create traffic log directory: {e}")
    
    def _get_log_filename(self, date: datetime = None) -> Path:
        """Get log filename for specific date"""
        if date is None:
            date = datetime.utcnow()
        
        date_str = date.strftime("%Y-%m-%d")
        return self.log_dir / f"traffic-{date_str}.log"
    
    def _hash_ip(self, ip: str) -> str:
        """Hash IP address for privacy"""
        if not traffic_config.HASH_IP_ADDRESSES:
            return ip
        
        # Use SHA256 with a salt for consistent hashing
        salt = "certalert_traffic_salt_2025"
        return hashlib.sha256((ip + salt).encode()).hexdigest()[:16]
    
    def _extract_client_ip(self, request: Request) -> str:
        """Extract real client IP from request headers"""
        # Check for forwarded headers first (proxy/load balancer)
        forwarded_for = request.headers.get('x-forwarded-for')
        if forwarded_for:
            # Take the first IP in the chain (original client)
            return forwarded_for.split(',')[0].strip()
        
        # Check for other common proxy headers
        real_ip = request.headers.get('x-real-ip')
        if real_ip:
            return real_ip.strip()
        
        # Fallback to direct client IP
        if hasattr(request, 'client') and request.client:
            return request.client.host
        
        return "unknown"
    
    def _should_log_request(self, request: Request) -> bool:
        """Determine if request should be logged"""
        if not traffic_config.ENABLED:
            return False
        
        path = request.url.path.lower()
        
        # Check excluded paths
        if any(path.startswith(excluded.lower()) for excluded in traffic_config.EXCLUDED_PATHS):
            return False
        
        # Check excluded file extensions
        if any(path.endswith(ext.lower()) for ext in traffic_config.EXCLUDED_EXTENSIONS):
            return False
        
        # Check excluded IPs
        client_ip = self._extract_client_ip(request)
        if client_ip in traffic_config.EXCLUDED_IPS:
            return False
        
        return True
    
    def _create_log_entry(self, request: Request, response_status: int = None, 
                         response_time_ms: float = None, user_id: Optional[int] = None) -> Dict[str, Any]:
        """Create a structured log entry"""
        client_ip = self._extract_client_ip(request)
        
        entry = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "ip": self._hash_ip(client_ip),
            "path": request.url.path,
            "method": request.method,
            "status": response_status,
            "duration_ms": round(response_time_ms, 2) if response_time_ms else None,
            "user_agent": request.headers.get("user-agent", ""),
            "referer": request.headers.get("referer", ""),
            "user_id": user_id
        }
        
        # Remove None values to keep logs clean
        return {k: v for k, v in entry.items() if v is not None}
    
    async def log_request(self, request: Request, response_status: int = None, 
                         response_time_ms: float = None, user_id: Optional[int] = None):
        """Log a request asynchronously"""
        try:
            if not self._should_log_request(request):
                return
            
            log_entry = self._create_log_entry(request, response_status, response_time_ms, user_id)
            log_filename = self._get_log_filename()
            
            # Write to file asynchronously
            loop = asyncio.get_event_loop()
            await loop.run_in_executor(None, self._write_log_entry, log_filename, log_entry)
            
        except Exception as e:
            logger.error(f"Failed to log traffic entry: {e}")
    
    def _write_log_entry(self, log_filename: Path, log_entry: Dict[str, Any]):
        """Write log entry to file (synchronous)"""
        try:
            with open(log_filename, 'a', encoding='utf-8') as f:
                json.dump(log_entry, f, separators=(',', ':'))
                f.write('\n')
        except Exception as e:
            logger.error(f"Failed to write log entry to {log_filename}: {e}")
    
    def cleanup_old_logs(self):
        """Clean up logs older than retention period"""
        try:
            cutoff_date = datetime.utcnow() - timedelta(days=traffic_config.RETENTION_DAYS)
            
            for log_file in self.log_dir.glob("traffic-*.log"):
                try:
                    # Extract date from filename
                    date_str = log_file.stem.replace("traffic-", "")
                    file_date = datetime.strptime(date_str, "%Y-%m-%d")
                    
                    if file_date < cutoff_date:
                        log_file.unlink()
                        logger.info(f"Deleted old traffic log: {log_file.name}")
                        
                except (ValueError, OSError) as e:
                    logger.warning(f"Failed to process log file {log_file}: {e}")
                    
        except Exception as e:
            logger.error(f"Failed to cleanup old logs: {e}")
    
    def get_available_log_dates(self) -> list:
        """Get list of available log dates"""
        dates = []
        try:
            for log_file in sorted(self.log_dir.glob("traffic-*.log")):
                try:
                    date_str = log_file.stem.replace("traffic-", "")
                    dates.append(date_str)
                except ValueError:
                    continue
        except Exception as e:
            logger.error(f"Failed to get available log dates: {e}")
        
        return dates

# Global traffic logger instance
traffic_logger = TrafficLogger()
