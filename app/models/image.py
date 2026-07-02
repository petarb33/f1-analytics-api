from sqlalchemy import Column, Integer, String, DateTime, LargeBinary
from datetime import datetime
from app.database.db import Base


class Image(Base):
    __tablename__ = "images"

    id = Column(Integer, primary_key=True)
    filename = Column(String, nullable=False)
    mime_type = Column(String, nullable=False)
    data = Column(LargeBinary, nullable=False)
    created_at = Column(DateTime, default=datetime.now)
