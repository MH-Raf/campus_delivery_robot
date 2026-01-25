from __future__ import annotations
from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Optional, Tuple

CAMPUS_MAP = {
    "Корпус A": (700.0, 0.0),
    "Корпус B": (1000.0, 500.0),
    "Общежитие": (200.0, 1200.0),
    "Столовая": (700.0, 400.0),
    "Лабораторный корпус": (1200.0, 300.0),
}

@dataclass
class RobotState:
    position: Tuple[float, float] = (0.0, 0.0)
    speed: float = 0.0
    speed_units: str = "m/s"
    busy: bool = False

@dataclass
class Order:
    address: str
    delivery_window: str
    confirmation_code: str
    status: str = "pending"
    eta: Optional[datetime] = None
    delivered_at: Optional[datetime] = None

class PositionSensor:
    def __init__(self, state: RobotState):
        self._state = state
    def read(self) -> Tuple[float, float]:
        return self._state.position

class Drive:
    def __init__(self, state: RobotState):
        self._state = state
        self.target: Optional[Tuple[float, float]] = None
    def command(self, target: Tuple[float, float]):
        self.target = target
    def update(self, dt: float = 1.0):
        if not self.target:
            return
        x, y = self._state.position
        tx, ty = self.target
        dx, dy = tx - x, ty - y
        dist = (dx*dx + dy*dy)**0.5
        if dist < 0.01:
            self._state.position = self.target
            return
        max_step = self._state.speed * dt
        step = min(max_step, dist)
        nx = x + dx / dist * step
        ny = y + dy / dist * step
        self._state.position = (nx, ny)

class Scheduler:
    def plan(self, position: Tuple[float, float], order: Order):
        # Проверка адреса
        if order.address not in CAMPUS_MAP:
            raise ValueError(
                f"Неизвестный адрес: {order.address}. Возможные варианты: {list(CAMPUS_MAP.keys())}"
            )

        dest = CAMPUS_MAP[order.address]

        # Безопасный парсинг окна доставки
        try:
            start, end = order.delivery_window.replace("–", "-").split("-")
        except ValueError:
            raise ValueError("Неверный формат окна доставки. Используйте формат 'HH:MM-HH:MM'.")

        today = datetime.now().date()

        try:
            t_start = datetime.strptime(start.strip(), "%H:%M").replace(
                year=today.year, month=today.month, day=today.day
            )
            t_end = datetime.strptime(end.strip(), "%H:%M").replace(
                year=today.year, month=today.month, day=today.day
            )
        except:
            raise ValueError("Время указано неверно. Используйте формат HH:MM.")

        if t_start >= t_end:
            raise ValueError("Начало окна доставки должно быть раньше конца.")

        midpoint = t_start + (t_end - t_start) / 2

        if midpoint < datetime.now():
            raise ValueError("Окно доставки уже прошло. Укажите более позднее время.")

        # Расчёт скорости
        dist = ((position[0]-dest[0])**2 + (position[1]-dest[1])**2)**0.5
        mins_to_mid = (midpoint - datetime.now()).total_seconds()/60

        if mins_to_mid > 1:
            desired_speed = dist / max(1e-3, mins_to_mid * 60)
            speed = max(0.2, min(2.0, desired_speed))
        else:
            speed = 1.5

        if speed <= 0:
            raise ValueError("Расчётная скорость робота некорректна.")

        eta = datetime.now() + timedelta(seconds=dist / max(1e-6, speed))
        order.eta = eta

        return {
            "route": [position, dest],
            "eta": eta,
            "speed": speed,
            "speed_units": "m/s"
        }


class Controller:
    def __init__(self, sensor: PositionSensor, scheduler: Scheduler, drive: Drive, state: RobotState):
        self.sensor = sensor
        self.scheduler = scheduler
        self.drive = drive
        self.state = state
    def accept_order(self, order: Order):
        pos = self.sensor.read()
        plan = self.scheduler.plan(pos, order)
        self.state.speed = plan["speed"]
        self.state.speed_units = plan["speed_units"]
        self.drive.command(plan["route"][-1])
        self.state.busy = True
        order.status = "in_progress"
        return plan
    def tick(self, dt: float = 1.0):
        self.drive.update(dt)
        if self.drive.target and self.state.position == self.drive.target:
            self.state.busy = False

class CourierRobot:
    def __init__(self):
        self.state = RobotState()
        self.sensor = PositionSensor(self.state)
        self.drive = Drive(self.state)
        self.scheduler = Scheduler()
        self.controller = Controller(self.sensor, self.scheduler, self.drive, self.state)
        self.current_order: Optional[Order] = None
    def create_order(self, address: str, window: str) -> Order:
        order = Order(address, window, confirmation_code="1234")
        self.current_order = order
        return order
    def accept_order(self, order: Order):
        return self.controller.accept_order(order)
    def deliver(self, code: str):
        if not self.current_order:
            raise RuntimeError("Заказ отсутствует")
        if code != self.current_order.confirmation_code:
            raise ValueError("Неверный код подтверждения")
        self.current_order.status = "delivered"
        self.current_order.delivered_at = datetime.now()
        return {"status": self.current_order.status,"delivered_at": self.current_order.delivered_at}
    def step(self, dt: float = 1.0):
        self.controller.tick(dt=dt)

# глобальный робот
robot = CourierRobot()

def scenario_a_sync():
    """Сценарий A — создать и принять заказ (синхронный helper)."""
    order = robot.create_order("Корпус B", "10:00–10:30")
    plan = robot.accept_order(order)
    return {"order": order, "plan": plan}


async def scenario_b_async(step_delay: float = 1.0):
    """Сценарий B — эмуляция движения и попытка доставки."""
    import asyncio
    while robot.state.busy:
        robot.step(dt=step_delay)
        await asyncio.sleep(step_delay)
    try:
        result = robot.deliver("1234")
        return result
    except Exception as e:
        return {"error": str(e)}