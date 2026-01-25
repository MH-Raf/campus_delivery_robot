from __future__ import annotations
from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Optional, Tuple

CAMPUS_MAP = {
    "Корпус A": (7.0, 0),
    "Корпус B": (10.0, 5.0),
    "Общежитие": (2.0, 12.0),
    "Столовая": (7.0, 4.0),
    "Лабораторный корпус": (12.0, 3.0),
}


@dataclass
class RobotState:
    position: Tuple[float, float] = (0.0, 0.0)
    speed: float = 1.0           # км/ч
    speed_units: str = "км/ч"
    busy: bool = False


@dataclass
class Order:
    address: str
    delivery_window: str
    confirmation_code: str
    status: str = "pending"
    eta: Optional[datetime] = None
    delivered_at: Optional[datetime] = None

    def __repr__(self) -> str:
        return (
            f"<Order {self.address} status={self.status} "
            f"eta={self.eta.strftime('%H:%M:%S') if self.eta else '-'}>"
        )


class PositionSensor:
    """Сенсор положения робота."""

    def __init__(self, state: RobotState):
        self._state = state

    def read(self) -> Tuple[float, float]:
        return self._state.position


class Drive:
    """Исполнитель движения робота."""

    def __init__(self, state: RobotState):
        self._state = state
        self.target: Optional[Tuple[float, float]] = None

    def command(self, target: Tuple[float, float]) -> None:
        if not isinstance(target, tuple) or len(target) != 2:
            raise ValueError("Цель должна быть кортежем (x, y)")
        self.target = target

    def update(self) -> None:
        """Эмуляция движения — шаг в сторону цели."""
        if not self.target:
            return

        x, y = self._state.position
        tx, ty = self.target
        dx, dy = tx - x, ty - y
        dist = (dx * dx + dy * dy) ** 0.5

        if dist < 0.01:
            self._state.position = self.target
            return

        m_per_min = (self._state.speed * 1000) / 60
        step = m_per_min / 60  

        self._state.position = (x + dx / dist * step, y + dy / dist * step)


class Scheduler:
    def plan(self, position: Tuple[float, float], order: Order):
        if order.address not in CAMPUS_MAP:
            raise ValueError("Неизвестный адрес")

        dest = CAMPUS_MAP[order.address]

        start, end = order.delivery_window.split("–")
        today = datetime.now().date()
        t_start = datetime.strptime(start, "%H:%M").replace(year=today.year, month=today.month, day=today.day)
        t_end = datetime.strptime(end, "%H:%M").replace(year=today.year, month=today.month, day=today.day)
        midpoint = t_start + (t_end - t_start) / 2

        dist = ((position[0] - dest[0]) ** 2 + (position[1] - dest[1]) ** 2) ** 0.5
        mins_to_mid = (midpoint - datetime.now()).total_seconds() / 60

        if mins_to_mid > 1:
            speed = max(0.5, min(3.0, dist / mins_to_mid))  # км/ч
        else:
            speed = 3.0

        speed_m_per_min = (speed * 1000) / 60
        eta = datetime.now() + timedelta(minutes=dist / speed_m_per_min)

        order.eta = eta

        return {
            "route": [position, dest],
            "eta": eta,
            "speed": speed,
            "speed_units": "км/ч",
        }


class Controller:
    """Связывает сенсор, планировщик и привод — центр логики."""

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

        return plan

    def tick(self):
        """Обновляет состояние робота на один шаг симуляции."""
        self.drive.update()
        if self.state.position == self.drive.target:
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

        dest = CAMPUS_MAP[self.current_order.address]
        x, y = self.state.position
        dx, dy = x - dest[0], y - dest[1]
        dist = (dx * dx + dy * dy) ** 0.5

        if dist > 0.5: 
            raise RuntimeError("Робот ещё в пути — доставка невозможна")

        self.current_order.status = "delivered"
        self.current_order.delivered_at = datetime.now()
        return {
            "status": self.current_order.status,
            "delivered_at": self.current_order.delivered_at,
        }

    def step(self):
        self.controller.tick()

### СЦЕНАРИИ

robot = CourierRobot()


def scenario_a():
    print("\n=== SCENARIO A: Принятие заказа ===")
    order = robot.create_order("Корпус B", "10:00–10:30")
    plan = robot.accept_order(order)

    print("Заказ:", order)
    print("Маршрут:", plan["route"])
    print("Скорость:", f"{plan['speed']:.2f} {plan['speed_units']}")
    print("ETA:", plan["eta"].strftime("%H:%M:%S"))


def scenario_b():
    print("\n=== SCENARIO B: Доставка ===")
    print("Эмуляция движения...")

    for _ in range(300):
        robot.step()

    try:
        result = robot.deliver("1234")
    except Exception as e:
        print("Ошибка:", e)
        return

    print("Статус:", result["status"])
    print("Время доставки:", result["delivered_at"].strftime("%H:%M:%S"))


if __name__ == "__main__":
    scenario_a()
    scenario_b()
