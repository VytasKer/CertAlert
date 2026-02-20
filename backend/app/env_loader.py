# backend/app/env_loader.py

import os
from pathlib import Path
from dotenv import load_dotenv


def load_env() -> str | None:
    env_name = (
        os.getenv("ENVIRONMENT")
        or os.getenv("ENV")
        or os.getenv("APP_ENV")
        or ""
    ).lower()

    project_root = Path(__file__).resolve().parents[2]

    if env_name.startswith("prod"):
        candidates = [
            project_root / ".env.production.local",
            project_root / ".env.production",
            project_root / ".env.local",
            project_root / ".env",
        ]
    else:
        candidates = [
            project_root / ".env.local",
            project_root / ".env",
            project_root / ".env.production.local",
            project_root / ".env.production",
        ]

    for path in candidates:
        if path.exists():
            load_dotenv(dotenv_path=str(path), override=False)
            return str(path)

    load_dotenv()
    return None
