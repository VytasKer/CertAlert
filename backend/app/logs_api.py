import os
from pathlib import Path
from fastapi import APIRouter, HTTPException

router = APIRouter(prefix="/logs", tags=["Logs"])

@router.get("/app-log")
def get_app_log():
    # Use new app log location
    log_path = Path(__file__).parent.parent / "logs" / "app" / "app.log"
    
    # Fallback to old location if new one doesn't exist yet
    if not log_path.exists():
        old_log_path = Path(__file__).parent.parent / "app.log"
        if old_log_path.exists():
            log_path = old_log_path
    
    if not log_path.exists():
        raise HTTPException(status_code=404, detail="Log file not found.")
    
    try:
        with open(log_path, "r", encoding="utf-8") as f:
            content = f.read()
        return {"log": content}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to read log file: {str(e)}")
