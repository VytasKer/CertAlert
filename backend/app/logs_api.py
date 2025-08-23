import os
from fastapi import APIRouter, HTTPException

router = APIRouter(prefix="/logs", tags=["Logs"])

@router.get("/app-log")
def get_app_log():
    log_path = os.path.join(os.path.dirname(__file__), "..", "app.log")
    log_path = os.path.abspath(log_path)
    if not os.path.exists(log_path):
        raise HTTPException(status_code=404, detail="Log file not found.")
    with open(log_path, "r", encoding="utf-8") as f:
        content = f.read()
    return {"log": content}
