import asyncio
import datetime
import json
import logging
import os

from src.bd.database import SessionLocal, redis_client
from src.bd.models import ImageModel
from src.log_config import setup_logging
from src.settings import settings


async def save_image() -> None:
    logging.debug("Starting mage_saver.py script...")

    if not os.path.exists(settings.processed_images_dir):
        os.makedirs(settings.processed_images_dir)

    while True:
        try:
            _, message = await redis_client.brpop("processed_image_queue")  # type: ignore

            data = json.loads(message)
            image_id = data["id"]
            image_data = bytes.fromhex(data["image_data"])
            description = data["description"]
            timestamp = data["timestamp"]

            image_filename = f"{image_id}.jpg"
            image_path = os.path.join(settings.processed_images_dir, image_filename)

            with open(image_path, "wb") as f:
                f.write(image_data)

            async with SessionLocal() as db:
                image_entry = ImageModel(
                    description=description,
                    timestamp=datetime.datetime.fromisoformat(timestamp),
                    image_path=image_path,
                )
                db.add(image_entry)
                await db.commit()
                await db.refresh(image_entry)

            logging.info(
                f"Изображение {image_id} сохранено в {image_path} и информация записана в БД."
            )

        except Exception as e:
            logging.error(f"Ошибка при сохранении изображения: {e}")


async def main() -> None:
    setup_logging()
    await save_image()


if __name__ == "__main__":
    asyncio.run(main())
