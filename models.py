from sqlalchemy import Column, Integer, String, Text, DateTime, Float
from datetime import datetime
from database import Base

class AuditLog(Base):
    __tablename__ = "audit_logs"

    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(DateTime, default=datetime.utcnow)
    user_query = Column(Text, nullable=False)
    ai_response = Column(Text, nullable=False)
    sources_cited = Column(Text, nullable=True) # Stored as a comma-separated string or JSON
    processing_time_ms = Column(Float, nullable=True)