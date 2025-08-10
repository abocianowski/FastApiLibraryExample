from core.db.session import SessionLocal
from typing import Generator, Optional

def get_db() -> Generator:
    db: Optional[SessionLocal] = None
    try:
        db = SessionLocal()
        yield db
    finally:
        if db:
            db.close()
