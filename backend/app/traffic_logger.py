# backend/app/traffic_logger.py

import json
import hashlib
import asyncio
from datetime import datetime, timedelta, date
from typing import Dict, Any, Optional
import logging
import os
from fastapi import Request
from sqlalchemy.orm import Session

from traffic_config import traffic_config
from app.database import SessionLocal
from app.models import TrafficLog

# Configure logging for traffic system
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("traffic_logger")

class TrafficLogger:
    """Handles traffic logging to database only"""
    
    def __init__(self):
        logger.info("Traffic logger initialized (database-only mode)")
    
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
        """Log a request asynchronously to database only"""
        try:
            if not self._should_log_request(request):
                return
            
            log_entry = self._create_log_entry(request, response_status, response_time_ms, user_id)
            
            # Write to database asynchronously
            loop = asyncio.get_event_loop()
            await loop.run_in_executor(None, self._write_to_database, log_entry)
            
        except Exception as e:
            logger.error(f"Failed to log traffic entry: {e}")
    
    def _write_to_database(self, log_entry: Dict[str, Any]):
        """Write log entry to database (synchronous)"""
        try:
            db = SessionLocal()
            try:
                # Parse timestamp
                timestamp_str = log_entry.get('timestamp', '')
                if timestamp_str.endswith('Z'):
                    timestamp_str = timestamp_str[:-1]  # Remove Z
                timestamp = datetime.fromisoformat(timestamp_str)
                
                # Create database entry
                traffic_log = TrafficLog(
                    timestamp=timestamp,
                    date=timestamp.date(),
                    log_data=log_entry,
                    ip_hash=log_entry.get('ip'),
                    path=log_entry.get('path'),
                    status_code=log_entry.get('status_code')
                )
                
                db.add(traffic_log)
                db.commit()
                
            finally:
                db.close()
                
        except Exception as e:
            logger.error(f"Failed to write log entry to database: {e}")
    
    def cleanup_old_logs(self):
        """Clean up logs older than retention period from database"""
        try:
            cutoff_date = datetime.utcnow() - timedelta(days=traffic_config.RETENTION_DAYS)
            
            # Clean up database entries only
            self._cleanup_database_logs(cutoff_date)
                    
        except Exception as e:
            logger.error(f"Failed to cleanup old logs: {e}")
    
    def _cleanup_database_logs(self, cutoff_date: datetime):
        """Clean up old traffic logs from database"""
        try:
            db = SessionLocal()
            try:
                # Delete logs older than cutoff date
                deleted_count = db.query(TrafficLog).filter(
                    TrafficLog.timestamp < cutoff_date
                ).delete()
                
                db.commit()
                logger.info(f"Deleted {deleted_count} old traffic log entries from database")
                
            finally:
                db.close()
                
        except Exception as e:
            logger.error(f"Failed to cleanup database logs: {e}")

# Global traffic logger instance
traffic_logger = TrafficLogger()
