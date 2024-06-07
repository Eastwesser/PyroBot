from datetime import datetime

from sqlalchemy import Column, String, DateTime
from sqlalchemy.orm import declarative_base

Base = declarative_base()


class User(Base):
    __tablename__ = 'users'

    id = Column(String, primary_key=True)  # Ensure this is a string to store UUIDs
    created_at = Column(DateTime, default=datetime.utcnow)
    status = Column(String, default='alive')
    status_updated_at = Column(DateTime, default=datetime.utcnow)
