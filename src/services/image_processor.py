import asyncio
import io
import json
import logging

from PIL import Image, ImageDraw, ImageFont

from src.bd.database import redis_client
from src.log_config import setup_logging
from src.settings import settings


async def process_image() -> None:
    logging.debug("Starting image_processor.py script...")

    while True:
        try:
            _, message = await redis_client.brpop("image_queue")  # type: ignore

            data = json.loads(message)
            image_id = data["id"]
            image_data = bytes.fromhex(data["image_data"])
            description = data["description"]
            timestamp = data["timestamp"]

            image = Image.open(io.BytesIO(image_data))

            font = ImageFont.truetype(settings.font_path, settings.font_size)

            max_text_width = image.width - 20

            def wrap_text(text: str, font: ImageFont.FreeTypeFont, max_width: int) -> list[str]:
                words = text.split()
                lines = []
                line = ""
                for word in words:
                    if line:
                        test_line = line + " " + word
                    else:
                        test_line = word
                    line_width = font.getmask(test_line).size[0]  # type: ignore
                    if line_width <= max_width:
                        line = test_line
                    else:
                        lines.append(line)
                        line = word
                if line:
                    lines.append(line)
                return lines

            lines = wrap_text(description, font, max_text_width)

            ascent, descent = font.getmetrics()
            line_height = ascent + descent

            padding_top = 10
            padding_bottom = 10

            total_text_height = line_height * len(lines)

            text_height = total_text_height + padding_top + padding_bottom

            new_image_height = image.height + text_height
            new_image = Image.new("RGB", (image.width, new_image_height), color="black")
            new_image.paste(image, (0, 0))

            draw = ImageDraw.Draw(new_image)

            y_text = image.height + padding_top

            x_text = 10

            for line in lines:
                draw.text((x_text, y_text), line, font=font, fill=(255, 255, 255))
                y_text += line_height

            img_byte_arr = io.BytesIO()
            new_image.save(img_byte_arr, format="JPEG")
            img_byte_arr = img_byte_arr.getvalue()  # type: ignore

            processed_message = {
                "id": image_id,
                "image_data": img_byte_arr.hex(),  # type: ignore
                "description": description,
                "timestamp": timestamp,
            }

            await redis_client.lpush(
                "processed_image_queue", json.dumps(processed_message)  # type: ignore
            )

            logging.info(f"Изображение {image_id} успешно обработано.")

        except Exception as e:
            logging.error(f"Ошибка при обработке изображения: {e}")


async def main() -> None:
    setup_logging()
    await process_image()


if __name__ == "__main__":
    asyncio.run(main())
