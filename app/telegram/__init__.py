import importlib.util
import inspect
import os
import secrets
from typing import Annotated

from aiogram import BaseMiddleware, Bot, Dispatcher
from aiogram.client.session.aiohttp import AiohttpSession
from aiogram.fsm.storage.base import DefaultKeyBuilder
from aiogram.fsm.storage.mongo import MongoStorage
from fastapi import FastAPI, Header

from app.core.config import cfg
from app.core.logger import get_logger

logger = get_logger("telegram")

session = AiohttpSession(proxy=(cfg.PROXY_URL or None))

dp = Dispatcher(
    storage=MongoStorage.from_url(
        url=cfg.MONGODB_URI,
        key_builder=DefaultKeyBuilder(with_destiny=True),
        db_name=f"{cfg.get_mongodb_db_name()}_telegram_fsm"
    )
)

bot = Bot(token=cfg.TELEGRAM_API_TOKEN, session=session)

telegram_webhook_url = f"{str(cfg.APP_BASE_URL).strip('/')}{cfg.TELEGRAM_WEBHOOK_PATH}"
telegram_webhook_secret = secrets.token_urlsafe(20)


def find_and_import_routers(directory):
    routers = {}
    for root, dirs, files in os.walk(directory):
        for file in files:
            if not file.endswith(".py"):
                continue
            file_path = os.path.join(root, file)
            spec = importlib.util.spec_from_file_location(file.replace('.py', ''), file_path)
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            routers[file_path] = getattr(module, 'router', None)

    return routers


def find_and_import_middlewares(directory):
    middleware_objects = {}

    for root, dirs, files in os.walk(directory):
        for file in files:
            if file.endswith('.py'):
                file_path = os.path.join(root, file)
                module_name = os.path.splitext(os.path.basename(file_path))[0]
                spec = importlib.util.spec_from_file_location(module_name, file_path)
                module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(module)
                for name, obj in vars(module).items():
                    if inspect.isclass(obj) and issubclass(obj, BaseMiddleware) and obj is not BaseMiddleware:
                        middleware_objects[file_path] = obj

    return middleware_objects


async def telegram_webhook_route(
        update: dict, x_telegram_bot_api_secret_token: Annotated[str | None, Header()] = None) -> None | dict:
    if x_telegram_bot_api_secret_token != telegram_webhook_secret:
        return {"status": "error", "message": "Wrong secret token !"}
    await dp.feed_webhook_update(bot=bot, update=update)


async def setup_telegram(app: FastAPI):
    logger.info("Setting up bot 🛠")

    # loading middlewares
    middlewares = find_and_import_middlewares('app/telegram/middlewares')
    for file, middleware in middlewares.items():
        if not middleware:
            logger.warning("No middleware found in [red]{file}[/red]")
            continue

        dp.update.middleware(middleware())
        logger.warning(f"{middleware.__name__} loaded from [blue]{file}[/blue]")

    # loading routers
    routers = find_and_import_routers('app/telegram/handlers')
    for file, router in routers.items():
        if not router:
            logger.warning(f"No router found in [red]{file}[/red]")
            continue

        dp.include_router(router)
        logger.warning(f"Router loaded from [blue]{file}[/blue]")

    # setup telegram webhook
    await bot.set_webhook(telegram_webhook_url,
                          drop_pending_updates=True,
                          secret_token=telegram_webhook_secret)

    app.add_api_route(cfg.TELEGRAM_WEBHOOK_PATH, telegram_webhook_route, methods=["POST"])
    logger.info(f"Added route for webhook at: {cfg.TELEGRAM_WEBHOOK_PATH}")

    logger.info("Webhook successfully set at: "
                f"[bright_black]{telegram_webhook_url}[/bright_black]")

    me = await bot.get_me()
    logger.info(f"Bot setup complete. Username: [cyan]@{me.username}[/cyan] 🤖")
