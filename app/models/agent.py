from sqlalchemy import Column, Integer, String, DateTime
from app.db.base import Base
from datetime import datetime, timezone

class PromptEngineeredAgent(Base):
    __tablename__ = "PromptEngineeredAgent"
    id = Column(Integer, primary_key=True, index=True)
    agentName = Column(String, index=True)
    description = Column(String)
    system = Column(String)
    responseTemplate = Column(String)
    trainingPrompts = Column(String)
    createdDate = Column(DateTime, default=datetime.now(timezone.utc))
    updatedDate = Column(DateTime, default=datetime.now(timezone.utc), onupdate=datetime.now(timezone.utc))

