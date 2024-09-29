import pytest
from httpx import AsyncClient
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession


@pytest.mark.asyncio
async def test_get_images(async_client: AsyncClient, db_session: AsyncSession) -> None:
    await db_session.execute(
        text(
            'INSERT INTO "images" (description, image_path) '
            "VALUES ('Test Image', '/tmp/test_image.jpg')"
        )
    )

    await db_session.commit()

    response = await async_client.get("/api/images")

    assert response.status_code == 200
    images = response.json()
    assert isinstance(images, list)
    assert len(images) > 0
    assert images[0]["description"] == "Test Image"
