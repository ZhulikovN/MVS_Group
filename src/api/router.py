import datetime
import json
import logging
import uuid
from typing import Annotated, List, Sequence

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile
from fastapi.responses import FileResponse
from redis.asyncio import RedisError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from src.bd import database
from src.bd.dto import ImageInfo
from src.bd.models import ImageModel

router = APIRouter()

CommonsDep = Annotated[AsyncSession, Depends(database.get_db)]


@router.post("/api/images")
async def upload_image(
    image: UploadFile = File(..., description="JPEG изображение"),
    description: str = Form(..., max_length=200, description="Описание изображения"),
) -> dict[str, str]:
    if image.content_type != "image/jpeg":
        raise HTTPException(status_code=400, detail="Формат файла должен быть JPEG")

    try:
        image_data = await image.read()

        image_id = str(uuid.uuid4())

        timestamp = datetime.datetime.now().isoformat()

        message = {
            "id": image_id,
            "image_data": image_data.hex(),
            "description": description,
            "timestamp": timestamp,
        }

        await database.redis_client.lpush("image_queue", json.dumps(message))  # type: ignore

        return {"message": "Изображение принято и отправлено на обработку."}

    except RedisError as re:
        logging.error(f"Ошибка при подключении к Redis: {re}")
        raise HTTPException(status_code=500, detail="Ошибка при работе с очередью")

    except Exception as e:
        logging.error(f"Ошибка при загрузке изображения: {e}")
        raise HTTPException(status_code=500, detail="Внутренняя ошибка сервера")


@router.get("/api/images", response_model=List[ImageInfo])
async def get_images(db: CommonsDep) -> Sequence[ImageModel]:
    try:
        result = await db.execute(select(ImageModel))
        images = result.scalars().all()
        return images
    except Exception as e:
        logging.error(f"Ошибка при получении изображений: {e}")
        raise HTTPException(
            status_code=500, detail="Ошибка при получении изображений из базы данных"
        )


@router.get("/api/images/{image_id}")
async def get_image(image_id: int, db: CommonsDep) -> FileResponse:
    try:
        result = await db.execute(select(ImageModel).filter(ImageModel.id == image_id))
        image = result.scalar()

        if image is None:
            raise HTTPException(status_code=404, detail="Изображение не найдено")

        return FileResponse(path=image.image_path, media_type="image/jpeg")

    except Exception as e:
        logging.error(f"Ошибка при получении изображения: {e}")
        raise HTTPException(status_code=500, detail="Ошибка при получении изображения")
