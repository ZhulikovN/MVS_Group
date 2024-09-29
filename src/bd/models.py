from sqlalchemy import Column, DateTime, Integer, String, func

from src.bd.database import Base


class ImageModel(Base):
    __tablename__ = "images"

    id = Column(Integer, primary_key=True, index=True)
    description = Column(String(200))
    timestamp = Column(DateTime(timezone=True), server_default=func.now())
    image_path = Column(String)
