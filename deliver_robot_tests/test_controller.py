import unittest
from unittest.mock import MagicMock
from campus_deliver_robot import Controller, PositionSensor, Scheduler, Drive, RobotState, Order


class TestController(unittest.TestCase):
    """Тесты для Controller с моками."""

    def setUp(self):
        self.state = RobotState()
        self.sensor = PositionSensor(self.state)
        self.drive = Drive(self.state)
        self.scheduler = Scheduler()
        self.controller = Controller(self.sensor, self.scheduler, self.drive, self.state)

    def tearDown(self):
        self.state = None
        self.sensor = None
        self.drive = None
        self.scheduler = None
        self.controller = None

    def test_accept_order_sets_state(self):
        """Проверка установки состояния после принятия заказа."""
        order = Order("Корпус B", "10:00–10:30")
        plan = self.controller.accept_order(order)
        self.assertTrue(self.state.busy)
        self.assertEqual(self.drive.target, plan["route"][-1])
        self.assertEqual(self.state.speed, plan["speed"])

    def test_accept_invalid_address(self):
        """Некорректный адрес вызывает ValueError."""
        order = Order("НЕСУЩЕСТВУЕТ", "10:00–10:30")
        with self.assertRaises(ValueError):
            self.controller.accept_order(order)

    def test_tick_moves_robot(self):
        """Робот двигается к цели после tick."""
        order = Order("Корпус B", "10:00–10:30")
        self.controller.accept_order(order)
        self.controller.tick(dt=1.0)
        self.assertNotEqual(self.state.position, (0.0, 0.0))

    def test_tick_reaches_target(self):
        """Робот достигает цели через несколько tick."""
        order = Order("Корпус B", "10:00–10:30")
        self.controller.accept_order(order)
        for _ in range(10000):
            self.controller.tick(dt=1.0)
            if not self.state.busy:
                break
        self.assertFalse(self.state.busy)
        self.assertEqual(self.state.position, self.drive.target)

    def test_mocked_sensor(self):
        """Используем мок для сенсора."""
        mock_sensor = MagicMock()
        mock_sensor.read.return_value = (50.0, 50.0)
        controller = Controller(mock_sensor, self.scheduler, self.drive, self.state)
        order = Order("Корпус B", "10:00–10:30")
        plan = controller.accept_order(order)
        self.assertEqual(plan["route"][0], (50.0, 50.0))


if __name__ == "__main__":
    unittest.main()
