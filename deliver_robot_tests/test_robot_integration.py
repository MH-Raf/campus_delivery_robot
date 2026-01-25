import unittest
from campus_deliver_robot import CourierRobot

class TestRobotIntegration(unittest.TestCase):
    """Интеграционные тесты для робота-курьера."""

    def setUp(self):
        self.robot = CourierRobot()

    def tearDown(self):
        self.robot = None

    def test_accept_order_and_delivery(self):
        """Принятие заказа, движение и успешная доставка."""
        order = self.robot.create_order("Корпус B", "10:00–10:30")
        self.robot.accept_order(order)
        for _ in range(10000):
            self.robot.step()
            if not self.robot.state.busy:
                break
        result = self.robot.deliver("1234")
        self.assertEqual(result["status"], "delivered")

    def test_delivery_with_wrong_code(self):
        """Ошибка при неверном коде."""
        order = self.robot.create_order("Корпус B", "10:00–10:30")
        self.robot.accept_order(order)
        for _ in range(10000):
            self.robot.step()
            if not self.robot.state.busy:
                break
        with self.assertRaises(ValueError):
            self.robot.deliver("0000")

    def test_delivery_too_far(self):
        """Ошибка, если робот ещё далеко."""
        order = self.robot.create_order("Корпус B", "10:00–10:30")
        self.robot.accept_order(order)
        with self.assertRaises(RuntimeError):
            self.robot.deliver("1234")
