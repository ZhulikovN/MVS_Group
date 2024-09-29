import io

import pytest
import redis.asyncio as redis
from httpx import AsyncClient

from src.bd import database


@pytest.mark.asyncio
async def test_upload_image(async_client: AsyncClient) -> None:
    database.redis_client = redis.Redis(host="localhost", port=6379, db=0)
    image_content = io.BytesIO(b"test image content")
    files = {"image": ("test_image.jpeg", image_content, "image/jpeg")}
    data = {"description": "Test Image"}

    response = await async_client.post("/api/images", files=files, data=data)

    assert response.status_code == 200
    assert response.json() == {"message": "Изображение принято и отправлено на обработку."}
    await database.redis_client.close()


@pytest.mark.asyncio
async def test_upload_invalid_image_format(async_client: AsyncClient) -> None:
    database.redis_client = redis.Redis(host="localhost", port=6379, db=0)
    image_content = io.BytesIO(b"test image content")
    files = {"image": ("test_image.png", image_content, "image/png")}
    data = {"description": "Test Image"}

    response = await async_client.post("/api/images", files=files, data=data)

    assert response.status_code == 400
    assert response.json() == {"detail": "Формат файла должен быть JPEG"}
    await database.redis_client.close()
