import os
import tempfile

import pytest
from httpx import AsyncClient
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession


@pytest.mark.asyncio
async def test_get_image_by_id(async_client: AsyncClient, db_session: AsyncSession) -> None:
    with tempfile.TemporaryDirectory() as temp_dir:
        file_path = os.path.join(temp_dir, "test_image.jpg")
        with open(file_path, "w") as f:
            f.write("Test image content")

        await db_session.execute(
            text(
                f'INSERT INTO "images" (description, image_path) '
                f"VALUES ('Test Image', '{file_path}')"
            )
        )

        await db_session.commit()

        result = await db_session.execute(
            text(
                "SELECT id FROM \"images\" WHERE description = 'Test Image' "
                "ORDER BY id DESC LIMIT 1"
            )
        )

        image_id = result.scalar()

        response = await async_client.get(f"/api/images/{image_id}")

        assert response.status_code == 200
        assert response.headers["content-type"] == "image/jpeg"


@pytest.mark.asyncio
async def test_get_image_not_found(async_client: AsyncClient) -> None:
    response = await async_client.get("/api/images/999999")

    assert response.status_code == 500
    assert response.json() == {"detail": "Ошибка при получении изображения"}
