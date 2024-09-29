import uvicorn

from src.api.app import app
from src.log_config import setup_logging
from src.settings import settings

if __name__ == "__main__":
    setup_logging()
    uvicorn.run(app, host=settings.API_HOST, port=settings.API_PORT)
