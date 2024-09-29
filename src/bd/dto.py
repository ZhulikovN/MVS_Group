from datetime import datetime

from pydantic import BaseModel


class ImageInfo(BaseModel):
    id: int
    description: str
    timestamp: datetime

    class Config:
        orm_mode = True
