from __future__ import annotations
from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Optional, Tuple

CAMPUS_MAP = {
    "Корпус A": (700, 0),
    "Корпус B": (1000, 500),
    "Общежитие": (200, 1200),
    "Столовая": (700, 400),
    "Лабораторный корпус": (1200, 300),
}


@dataclass
class RobotState:
    position: Tuple[float, float] = (0.0, 0.0)  
    speed: float = 0.0  
    busy: bool = False


class Order:
    """Заказ с адресом, окном доставки и кодом подтверждения."""

    def __init__(self, address: str, delivery_window: str, confirmation_code: str = "1234"):
        self.address = address
        self.delivery_window = delivery_window
        self.confirmation_code = confirmation_code
        self.status: str = "pending"
        self.eta: Optional[datetime] = None
        self.delivered_at: Optional[datetime] = None
        self.x: Optional[float] = None
        self.y: Optional[float] = None
        self.speed_mps: Optional[float] = None

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
        self.speed: float = 0.0  

    def command(self, target: Tuple[float, float], speed: float) -> None:
        if not isinstance(target, tuple) or len(target) != 2:
            raise ValueError("Цель должна быть кортежем (x, y)")
        self.target = target
        self.speed = speed

    def update(self, dt: float = 1.0) -> None:
        if self.target is None:
            return

        x, y = self._state.position
        tx, ty = self.target
        dx, dy = tx - x, ty - y
        dist = (dx * dx + dy * dy) ** 0.5

        if dist < 0.1:  
            self._state.position = self.target
            self._state.busy = False
            return

        step = self.speed * dt
        if step >= dist:
            self._state.position = self.target
            self._state.busy = False
            return

        new_x = x + dx / dist * step
        new_y = y + dy / dist * step
        self._state.position = (new_x, new_y)


class Scheduler:
    """Простейший планировщик."""

    def plan(self, position: Tuple[float, float], order: Order):
        if order.address not in CAMPUS_MAP:
            raise ValueError("Неизвестный адрес")

        dest = CAMPUS_MAP[order.address]
        order.x, order.y = dest

        start_str, end_str = order.delivery_window.split("–")
        today = datetime.now().date()
        t_start = datetime.strptime(start_str, "%H:%M").replace(year=today.year, month=today.month, day=today.day)
        t_end = datetime.strptime(end_str, "%H:%M").replace(year=today.year, month=today.month, day=today.day)
        midpoint = t_start + (t_end - t_start) / 2

        dist = ((position[0] - dest[0]) ** 2 + (position[1] - dest[1]) ** 2) ** 0.5

        mins_to_mid = (midpoint - datetime.now()).total_seconds() / 60
        if mins_to_mid > 1:
            speed_mps = max(0.6, min(3.0, dist / (mins_to_mid * 60)))
        else:
            speed_mps = 3.0  # м/с

        order.speed_mps = speed_mps
        meters_per_sec = speed_mps
        eta = datetime.now() + timedelta(seconds=dist / meters_per_sec)
        order.eta = eta

        return {
            "route": [position, dest],
            "eta": eta,
            "speed": speed_mps,
        }


class Controller:
    """Центр логики."""

    def __init__(self, sensor: PositionSensor, scheduler: Scheduler, drive: Drive, state: RobotState):
        self.sensor = sensor
        self.scheduler = scheduler
        self.drive = drive
        self.state = state

    def accept_order(self, order: Order):
        pos = self.sensor.read()
        plan = self.scheduler.plan(pos, order)

        self.state.speed = plan["speed"]
        self.drive.command(plan["route"][-1], self.state.speed)
        self.state.busy = True
        return plan

    def tick(self, dt: float = 1.0):
        self.drive.update(dt)


class CourierRobot:
    """Интегратор всего робота."""

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

        x, y = self.state.position
        tx, ty = self.current_order.x, self.current_order.y
        dist = ((x - tx) ** 2 + (y - ty) ** 2) ** 0.5

        if dist > 3.0:
            raise RuntimeError("Робот ещё в пути — доставка невозможна")

        self.current_order.status = "delivered"
        self.current_order.delivered_at = datetime.now()
        return {
            "status": self.current_order.status,
            "delivered_at": self.current_order.delivered_at,
        }

    def step(self):
        self.controller.tick()


# === СЦЕНАРИИ ===

def scenario_a(robot: CourierRobot):
    print("\n=== SCENARIO A: Принятие заказа ===")
    order = robot.create_order("Корпус B", "10:00–10:30")
    plan = robot.accept_order(order)
    print("Заказ:", order)
    print("Маршрут:", plan["route"])
    print("Скорость:", f"{plan['speed']:.2f} м/с")
    print("ETA:", plan["eta"].strftime("%H:%M:%S"))


def scenario_b(robot: CourierRobot):
    print("\n=== SCENARIO B: Доставка ===")
    print("Эмуляция движения...")
    for _ in range(5000):
        robot.step()
        if not robot.state.busy:
            break

    try:
        result = robot.deliver("1234")
    except Exception as e:
        print("Ошибка:", e)
        return

    print("Статус:", result["status"])
    print("Время доставки:", result["delivered_at"].strftime("%H:%M:%S"))


if __name__ == "__main__":
    robot = CourierRobot()
    scenario_a(robot)
    scenario_b(robot)
