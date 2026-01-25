from dataclasses import dataclass
from typing import Any, Optional
from campus_delivery_robot import CourierRobot, Order

@dataclass
class RobotStatus:
    name: str
    sensors: dict[str, Any]
    actuators: dict[str, Any]
    mode: str | None = None
    last_error: str | None = None

class RobotService:
    """Адаптер Telegram-бота под CourierRobot (ЛР1)."""

    def __init__(self) -> None:
        self.robot = CourierRobot()
        self._current_order: Optional[Order] = None
        self._last_error: Optional[str] = None

    def get_status(self) -> RobotStatus:
        state = self.robot.state
        sensors = {
            "position": f"{state.position[0]:.2f}, {state.position[1]:.2f}",
            "busy": state.busy,
        }
        actuators = {
            "speed": f"{state.speed:.2f} {state.speed_units}",
            "target": self.robot.drive.target,
        }
        mode = "busy" if state.busy else "idle"

        if self._current_order:
            sensors["order"] = self._current_order.address
            sensors["eta"] = (
                self._current_order.eta.strftime("%H:%M:%S")
                if self._current_order.eta
                else "-"
            )
            sensors["order_status"] = self._current_order.status

        return RobotStatus(
            name="Campus Courier Robot",
            sensors=sensors,
            actuators=actuators,
            mode=mode,
            last_error=self._last_error,
        )

    def create_order(self, address: str, window: str) -> str:
        try:
            window = window.replace("-", "–")
            order = self.robot.create_order(address, window)
            self.robot.accept_order(order)
            self._current_order = order
            return (
                f"Заказ принят: {order.address}, "
                f"ETA {order.eta.strftime('%H:%M:%S')}"
            )
        except Exception as e:
            self._last_error = str(e)
            return f"Ошибка создания заказа: {e}"

    def deliver_order(self, code: str) -> str:
        if not self._current_order:
            return "Нет активного заказа"
        try:
            result = self.robot.deliver(code)
            return (
                f"Доставка выполнена!\n"
                f"Статус: {result['status']}\n"
                f"Время доставки: {result['delivered_at'].strftime('%H:%M:%S')}"
            )
        except Exception as e:
            self._last_error = str(e)
            return f"Ошибка доставки: {e}"

    def stop(self) -> None:
        self.robot.drive.target = None
        self.robot.state.busy = False

    def set_param(self, param: str, value: str) -> str:
        if param == "speed":
            self.robot.state.speed = float(value)
            return f"Скорость установлена: {value} км/ч"
        raise ValueError(f"Неизвестный параметр: {param}")

    def get_param(self, param: str) -> str:
        if param == "speed":
            return f"speed = {self.robot.state.speed} км/ч"
        if param == "position":
            x, y = self.robot.state.position
            return f"position = ({x:.2f}, {y:.2f})"
        raise ValueError(f"Неизвестный параметр: {param}")
