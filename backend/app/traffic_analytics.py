# backend/app/traffic_analytics.py

import json
from datetime import datetime, timedelta, date
from pathlib import Path
from collections import defaultdict, Counter
from typing import Dict, Any, List, Optional
import logging
from sqlalchemy.orm import Session
from sqlalchemy import and_, func

from traffic_config import traffic_config
from app.database import SessionLocal
from app.models import TrafficLog

logger = logging.getLogger("traffic_analytics")

class TrafficAnalytics:
    """Traffic analytics processor using database storage"""
    
    def __init__(self):
        self.log_dir = Path(traffic_config.LOG_DIR)  # Keep for backward compatibility
    
    def _get_log_entries_for_date(self, target_date: date) -> List[Dict[str, Any]]:
        """Get log entries for a specific date from database"""
        entries = []
        
        try:
            db = SessionLocal()
            try:
                # Query database for entries on the specific date
                logs = db.query(TrafficLog).filter(
                    TrafficLog.date == target_date
                ).order_by(TrafficLog.timestamp).all()
                
                # Extract log_data from each entry
                entries = [log.log_data for log in logs]
                
            finally:
                db.close()
                
        except Exception as e:
            logger.error(f"Failed to get log entries for {target_date}: {e}")
            # Fallback to file-based reading if database fails
            entries = self._read_log_file(target_date.strftime("%Y-%m-%d"))
        
        return entries
    
    def _read_log_file(self, date_str: str) -> List[Dict[str, Any]]:
        """Read and parse a specific log file (fallback method)"""
        log_file = self.log_dir / f"traffic-{date_str}.log"
        entries = []
        
        try:
            if not log_file.exists():
                return entries
            
            with open(log_file, 'r', encoding='utf-8') as f:
                for line_num, line in enumerate(f, 1):
                    line = line.strip()
                    if not line:
                        continue
                    
                    try:
                        entry = json.loads(line)
                        entries.append(entry)
                    except json.JSONDecodeError as e:
                        logger.warning(f"Failed to parse line {line_num} in {log_file}: {e}")
                        
        except Exception as e:
            logger.error(f"Failed to read log file {log_file}: {e}")
        
        return entries
    
    def get_today_stats(self) -> Dict[str, Any]:
        """Get today's traffic statistics"""
        today = datetime.utcnow().date()
        return self.get_daily_stats(today.strftime("%Y-%m-%d"))
    
    def get_daily_stats(self, date_str: str) -> Dict[str, Any]:
        """Get traffic statistics for a specific date"""
        try:
            target_date = datetime.strptime(date_str, "%Y-%m-%d").date()
            entries = self._get_log_entries_for_date(target_date)
        except ValueError:
            return {"error": "Invalid date format"}
        
        if not entries:
            return {
                "date": date_str,
                "total_requests": 0,
                "unique_visitors": 0,
                "top_pages": [],
                "status_codes": {},
                "methods": {},
                "avg_response_time": 0,
                "hourly_distribution": {}
            }
        
        # Basic statistics
        total_requests = len(entries)
        unique_ips = set()
        paths = []
        status_codes = Counter()
        methods = Counter()
        response_times = []
        hourly_counts = defaultdict(int)
        
        for entry in entries:
            # Unique visitors (by IP)
            if 'ip' in entry:
                unique_ips.add(entry['ip'])
            
            # Page visits
            if 'path' in entry:
                paths.append(entry['path'])
            
            # Status codes
            if 'status' in entry:
                status_codes[entry['status']] += 1
            
            # HTTP methods
            if 'method' in entry:
                methods[entry['method']] += 1
            
            # Response times
            if 'duration_ms' in entry and entry['duration_ms'] is not None:
                response_times.append(entry['duration_ms'])
            
            # Hourly distribution
            if 'timestamp' in entry:
                try:
                    dt = datetime.fromisoformat(entry['timestamp'].replace('Z', '+00:00'))
                    hour = dt.hour
                    hourly_counts[hour] += 1
                except Exception:
                    pass
        
        # Calculate averages and top items
        avg_response_time = sum(response_times) / len(response_times) if response_times else 0
        top_pages = Counter(paths).most_common(10)
        
        return {
            "date": date_str,
            "total_requests": total_requests,
            "unique_visitors": len(unique_ips),
            "top_pages": [{"path": path, "count": count} for path, count in top_pages],
            "status_codes": dict(status_codes),
            "methods": dict(methods),
            "avg_response_time": round(avg_response_time, 2),
            "hourly_distribution": dict(hourly_counts)
        }
    
    def get_raw_logs(self, date_str: str) -> str:
        """Get raw log content for download from database"""
        try:
            target_date = datetime.strptime(date_str, "%Y-%m-%d").date()
            entries = self._get_log_entries_for_date(target_date)
            
            if not entries:
                return ""
            
            # Convert log entries back to JSON lines format
            lines = []
            for entry in entries:
                lines.append(json.dumps(entry, separators=(',', ':')))
            
            return '\n'.join(lines)
            
        except Exception as e:
            logger.error(f"Failed to get raw logs for {date_str}: {e}")
            # Fallback to file-based method
            log_file = self.log_dir / f"traffic-{date_str}.log"
            try:
                if log_file.exists():
                    with open(log_file, 'r', encoding='utf-8') as f:
                        return f.read()
            except Exception as file_error:
                logger.error(f"Failed to read raw logs from file for {date_str}: {file_error}")
            
            return ""
    
    def get_available_dates(self) -> List[str]:
        """Get list of available log dates from database"""
        dates = []
        try:
            db = SessionLocal()
            try:
                # Query distinct dates from database
                db_dates = db.query(TrafficLog.date).distinct().order_by(TrafficLog.date.desc()).all()
                dates = [date_row[0].strftime("%Y-%m-%d") for date_row in db_dates]
                
            finally:
                db.close()
                
        except Exception as e:
            logger.error(f"Failed to get available dates from database: {e}")
            # Fallback to file-based method
            try:
                for log_file in sorted(self.log_dir.glob("traffic-*.log"), reverse=True):
                    try:
                        date_str = log_file.stem.replace("traffic-", "")
                        # Validate date format
                        datetime.strptime(date_str, "%Y-%m-%d")
                        dates.append(date_str)
                    except ValueError:
                        continue
            except Exception as file_error:
                logger.error(f"Failed to get available dates from files: {file_error}")
        
        return dates
    
    def get_summary_stats(self, days: int = 7) -> Dict[str, Any]:
        """Get summary statistics for the last N days"""
        end_date = datetime.utcnow()
        total_requests = 0
        total_unique_visitors = set()
        all_paths = []
        
        for i in range(days):
            date = end_date - timedelta(days=i)
            date_str = date.strftime("%Y-%m-%d")
            
            daily_stats = self.get_daily_stats(date_str)
            total_requests += daily_stats["total_requests"]
            
            # For unique visitors, we need to read raw entries to get IP hashes
            entries = self._get_log_entries_for_date(date.date())
            for entry in entries:
                if 'ip' in entry:
                    total_unique_visitors.add(entry['ip'])
                if 'path' in entry:
                    all_paths.append(entry['path'])
        
        top_pages = Counter(all_paths).most_common(10)
        
        return {
            "period_days": days,
            "total_requests": total_requests,
            "unique_visitors": len(total_unique_visitors),
            "avg_daily_requests": round(total_requests / days, 1),
            "top_pages": [{"path": path, "count": count} for path, count in top_pages]
        }

# Global analytics instance
traffic_analytics = TrafficAnalytics()
