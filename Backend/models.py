from sqlalchemy import Column, Integer, String, Text, DateTime
from sqlalchemy.orm import declarative_base
from datetime import datetime

Base = declarative_base()

class MoodHistory(Base):
    __tablename__ = "mood_history"

    id = Column(Integer, primary_key=True, index=True)
    text = Column(Text, nullable=False)
    emotion = Column(String(50), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)