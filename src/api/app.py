from fastapi import FastAPI

from src.api.router import router
from src.settings import settings

app = FastAPI(title=settings.app_name)

app.include_router(router)
