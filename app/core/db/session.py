from core.config import DATABASE_URL
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

engine = create_engine(
    DATABASE_URL,
    connect_args={'application_name': 'Library API'},
    pool_size=10
)
SessionLocal = sessionmaker(autocommit=False, autoflush=True, bind=engine, future=True)