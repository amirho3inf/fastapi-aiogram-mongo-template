from aiogram import F, Router, types
from aiogram.filters import Command, CommandStart
from aiogram.types import Message
from aiogram.utils.markdown import hbold

router = Router()


@router.message(Command("id"))
async def cmd_id(message: Message) -> None:
    return await message.answer(f"Your ID: {message.from_user.id}")


@router.message(CommandStart())
async def cmd_start(message: Message) -> None:
    await message.answer(f"Hello, {hbold(message.from_user.full_name)}!")


@router.message(F.text == "echo")
async def echo(message: types.Message) -> None:
    try:
        await message.send_copy(chat_id=message.chat.id)
    except Exception as e:
        await message.answer("Nice try!")


@router.message(F.text == "ping")
async def hello(message: types.Message) -> None:
    try:
        await message.answer("pong")
    except Exception as e:
        await message.answer("Nice try!")
