import importlib
import os
from contextlib import asynccontextmanager

from fastapi import APIRouter, FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.routing import APIRoute
from fastapi_responses import custom_openapi

from app.core.config import cfg
from app.core.database import init_db
from app.core.logger import get_logger
from app.telegram import setup_telegram

routes_folder = 'app/routes'

logger = get_logger()


@asynccontextmanager
async def lifespan(app: FastAPI):
    # on start
    await init_db()
    await setup_telegram(app)

    yield

    # on stop
    pass

app = FastAPI(
    title=cfg.APP_TITLE,
    summary=cfg.APP_SUMMARY,
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allow all methods (GET, POST, etc.)
    allow_headers=["*"],  # Allow all headers
)


# load routes
for root, dirs, files in os.walk(routes_folder):
    for file in files:
        if file.endswith(".py") and file != "__init__.py":
            file_path = os.path.join(root, file)
            module_name = file_path.replace(routes_folder, "").replace('/', '.').replace('.py', '')

            if module_name.startswith('.'):
                module_name = f'{routes_folder.replace("/", ".")}{module_name}'

            module = importlib.import_module(module_name)

            for attribute_name in dir(module):
                attribute = getattr(module, attribute_name)
                if isinstance(attribute, APIRouter):
                    app.include_router(attribute)
                    logger.info(f"Router loaded from [blue]{file_path}[/blue]")

# custom openapi operation name
app.openapi = custom_openapi(app)
for route in app.routes:
    if isinstance(route, APIRoute):
        route.operation_id = route.name
