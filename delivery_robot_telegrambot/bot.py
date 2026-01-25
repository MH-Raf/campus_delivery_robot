import asyncio
import logging

from aiogram import Bot, Dispatcher
from aiogram.filters import Command
from aiogram.types import Message

from settings import load_settings
from robot_service import RobotService

logging.basicConfig(level=logging.INFO)

settings = load_settings()
bot = Bot(token=settings.bot_token)
dp = Dispatcher()
service = RobotService()



def format_status_text(status) -> str:
    lines = []
    lines.append(f"🤖 Robot: {status.name}")
    if status.mode is not None:
        lines.append(f"Mode: {status.mode}")
    lines.append("\nSensors:")
    for k, v in status.sensors.items():
        lines.append(f"- {k}: {v}")
    lines.append("\nActuators:")
    for k, v in status.actuators.items():
        lines.append(f"- {k}: {v}")
    if status.last_error:
        lines.append(f"\nLast error: {status.last_error}")
    return "\n".join(lines)



@dp.message(Command("start"))
async def start(m: Message):
    await m.answer(
        "Привет! Я бот управления роботом.\n"
        "Команды:\n"
        "/create_order <корпус> <HH:MM-HH:MM> — создать заказ\n"
        "/run_b <код> — доставка заказа по коду\n"
        "/status — статус робота\n"
        "/stop — аварийная остановка\n"
        "/set <param> <value>, /get <param>"
    )


@dp.message(Command("status"))
async def status_cmd(m: Message):
    try:
        status = service.get_status()
        await m.answer(format_status_text(status))
    except Exception as e:
        logging.exception("status failed")
        await m.answer(f"Ошибка получения статуса: {e}")


@dp.message(Command("create_order"))
async def create_order_cmd(m: Message):
    if not m.text:
        return
    parts = m.text.split(maxsplit=2)
    if len(parts) < 3:
        await m.answer("Формат: /create_order <корпус> <HH:MM-HH:MM>")
        return


    try:
        last_space = parts[2].rfind(" ")
        if last_space == -1:
            await m.answer("Неверный формат: укажите адрес и окно времени")
            return
        address = f"{parts[1]} {parts[2][:last_space]}".strip()
        window = parts[2][last_space + 1:].strip()
    except Exception:
        await m.answer("Ошибка разбора команды")
        return

    try:
        msg = service.create_order(address, window)
        await m.answer(msg)
    except Exception as e:
        await m.answer(f"Ошибка создания заказа: {e}")


@dp.message(Command("run_b"))
async def run_b_cmd(m: Message):
    if not m.text:
        await m.answer("Формат: /run_b <код подтверждения>")
        return
    parts = m.text.split(maxsplit=1)
    if len(parts) < 2:
        await m.answer("Формат: /run_b <код подтверждения>")
        return
    _, code = parts
    msg = await asyncio.to_thread(service.deliver_order, code)
    await m.answer(msg)


@dp.message(Command("stop"))
async def stop_cmd(m: Message):
    service.stop()
    await m.answer("Остановлено")


@dp.message(Command("set"))
async def set_cmd(m: Message):
    if not m.text:
        return
    parts = m.text.split(maxsplit=2)
    if len(parts) < 3:
        await m.answer("Формат: /set <param> <value>")
        return
    _, param, value = parts
    try:
        msg = service.set_param(param, value)
        await m.answer(msg)
    except Exception as e:
        await m.answer(f"Ошибка set: {e}")


@dp.message(Command("get"))
async def get_cmd(m: Message):
    if not m.text:
        return
    parts = m.text.split(maxsplit=1)
    if len(parts) < 2:
        await m.answer("Формат: /get <param>")
        return
    _, param = parts
    try:
        msg = service.get_param(param)
        await m.answer(msg)
    except Exception as e:
        await m.answer(f"Ошибка get: {e}")

async def robot_loop():
    while True:
        service.robot.step()
        await asyncio.sleep(0.1)  


async def main():
    asyncio.create_task(robot_loop())
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
