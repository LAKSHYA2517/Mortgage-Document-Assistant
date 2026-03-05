from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

# For local development, we use SQLite to get up and running instantly.
# 💡 DEPLOYMENT SWAP POINT: For production (Week 4), change this to your PostgreSQL URL:
# SQLALCHEMY_DATABASE_URL = "postgresql://username:password@localhost/mortgage_db"
SQLALCHEMY_DATABASE_URL = "sqlite:///./audit_log.db"

# connect_args is only needed for SQLite
engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()