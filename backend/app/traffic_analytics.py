# backend/app/traffic_analytics.py

import json
from datetime import datetime, timedelta
from pathlib import Path
from collections import defaultdict, Counter
from typing import Dict, Any, List, Optional
import logging

from traffic_config import traffic_config

logger = logging.getLogger("traffic_analytics")

class TrafficAnalytics:
    """Simple traffic analytics processor"""
    
    def __init__(self):
        self.log_dir = Path(traffic_config.LOG_DIR)
    
    def _read_log_file(self, date_str: str) -> List[Dict[str, Any]]:
        """Read and parse a specific log file"""
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
        today = datetime.utcnow().strftime("%Y-%m-%d")
        return self.get_daily_stats(today)
    
    def get_daily_stats(self, date_str: str) -> Dict[str, Any]:
        """Get traffic statistics for a specific date"""
        entries = self._read_log_file(date_str)
        
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
        """Get raw log content for download"""
        log_file = self.log_dir / f"traffic-{date_str}.log"
        
        try:
            if not log_file.exists():
                return ""
            
            with open(log_file, 'r', encoding='utf-8') as f:
                return f.read()
                
        except Exception as e:
            logger.error(f"Failed to read raw logs for {date_str}: {e}")
            return ""
    
    def get_available_dates(self) -> List[str]:
        """Get list of available log dates"""
        dates = []
        try:
            for log_file in sorted(self.log_dir.glob("traffic-*.log"), reverse=True):
                try:
                    date_str = log_file.stem.replace("traffic-", "")
                    # Validate date format
                    datetime.strptime(date_str, "%Y-%m-%d")
                    dates.append(date_str)
                except ValueError:
                    continue
        except Exception as e:
            logger.error(f"Failed to get available dates: {e}")
        
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
            entries = self._read_log_file(date_str)
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
