import importlib
import inspect
import os

import beanie
from motor.motor_asyncio import AsyncIOMotorClient

from app.core.config import cfg
from app.core.logger import get_logger

models_folder = "app/models"

logger = get_logger()

client = AsyncIOMotorClient(cfg.MONGODB_URI, tz_aware=True)
db_name = cfg.get_mongodb_db_name()


async def init_db():
    document_models = []

    for filename in os.listdir(models_folder):
        if filename.endswith(".py") and filename != "__init__.py":
            module_name = f"{models_folder.replace('/', '.')}.{filename[:-3]}"

            model_module = importlib.import_module(module_name)

            for attr_name in dir(model_module):
                attr = getattr(model_module, attr_name)

                if inspect.isclass(attr) and issubclass(attr, beanie.Document) and attr is not beanie.Document:
                    document_models.append(attr)

    logger.info(f"Loaded models: {[model.__name__ for model in document_models]}")

    await beanie.init_beanie(
        database=getattr(client, db_name),
        document_models=document_models
    )
