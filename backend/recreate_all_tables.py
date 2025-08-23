# backend/app/recreate_all_tables.py

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from app import database
from app import models

print("Dropping all tables...")
models.Base.metadata.drop_all(bind=database.engine)
print("Creating all tables...")
models.Base.metadata.create_all(bind=database.engine)
print("Done.")