# backend/app/traffic_api.py

from fastapi import APIRouter, HTTPException
from fastapi.responses import PlainTextResponse
from datetime import datetime
import logging

from app.traffic_analytics import traffic_analytics
from app.traffic_logger import traffic_logger

logger = logging.getLogger("traffic_api")

router = APIRouter(prefix="/admin/traffic", tags=["Traffic Analytics"])

# Note: These endpoints are protected by the OriginValidationMiddleware 
# which validates API keys for /admin/* routes

@router.get("/stats/today")
def get_today_stats():
    """Get today's traffic statistics"""
    try:
        stats = traffic_analytics.get_today_stats()
        return stats
    except Exception as e:
        logger.error(f"Failed to get today's stats: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve traffic statistics")

@router.get("/stats/{date}")
def get_daily_stats(date: str):
    """Get traffic statistics for a specific date (YYYY-MM-DD format)"""
    try:
        # Validate date format
        datetime.strptime(date, "%Y-%m-%d")
        stats = traffic_analytics.get_daily_stats(date)
        return stats
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid date format. Use YYYY-MM-DD")
    except Exception as e:
        logger.error(f"Failed to get stats for {date}: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve traffic statistics")

@router.get("/stats/summary/{days}")
def get_summary_stats(days: int):
    """Get summary statistics for the last N days"""
    try:
        if days < 1 or days > 90:
            raise HTTPException(status_code=400, detail="Days must be between 1 and 90")
        
        stats = traffic_analytics.get_summary_stats(days)
        return stats
    except Exception as e:
        logger.error(f"Failed to get summary stats for {days} days: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve traffic statistics")

@router.get("/logs/{date}", response_class=PlainTextResponse)
def download_raw_logs(date: str):
    """Download raw traffic logs for a specific date"""
    try:
        # Validate date format
        datetime.strptime(date, "%Y-%m-%d")
        logs = traffic_analytics.get_raw_logs(date)
        
        if not logs:
            raise HTTPException(status_code=404, detail=f"No logs found for {date}")
        
        return PlainTextResponse(
            content=logs,
            headers={
                "Content-Disposition": f"attachment; filename=traffic-{date}.log",
                "Content-Type": "text/plain"
            }
        )
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid date format. Use YYYY-MM-DD")
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to download logs for {date}: {e}")
        raise HTTPException(status_code=500, detail="Failed to download traffic logs")

@router.get("/dates")
def get_available_dates():
    """Get list of available log dates"""
    try:
        dates = traffic_analytics.get_available_dates()
        return {"available_dates": dates}
    except Exception as e:
        logger.error(f"Failed to get available dates: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve available dates")

@router.post("/cleanup")
def cleanup_old_logs():
    """Manually trigger cleanup of old log files"""
    try:
        traffic_logger.cleanup_old_logs()
        return {"message": "Log cleanup completed successfully"}
    except Exception as e:
        logger.error(f"Failed to cleanup logs: {e}")
        raise HTTPException(status_code=500, detail="Failed to cleanup logs")
