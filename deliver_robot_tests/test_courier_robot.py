import unittest
from campus_deliver_robot import CourierRobot, Order


class TestCourierRobot(unittest.TestCase):
    """Интеграционные тесты для CourierRobot."""

    def setUp(self):
        self.robot = CourierRobot()

    def tearDown(self):
        self.robot = None

    def test_create_order(self):
        """Создание заказа."""
        order = self.robot.create_order("Корпус B", "10:00–10:30")
        self.assertIsInstance(order, Order)
        self.assertEqual(self.robot.current_order, order)

    def test_accept_order_sets_target(self):
        """После accept_order цель задается."""
        order = self.robot.create_order("Корпус B", "10:00–10:30")
        plan = self.robot.accept_order(order)
        self.assertEqual(self.robot.drive.target, plan["route"][-1])

    def test_successful_delivery(self):
        """Успешная доставка после движения."""
        order = self.robot.create_order("Корпус B", "10:00–10:30")
        self.robot.accept_order(order)
        for _ in range(10000):
            self.robot.step()
            if not self.robot.state.busy:
                break
        result = self.robot.deliver("1234")
        self.assertEqual(result["status"], "delivered")

    def test_wrong_code_raises(self):
        """Неверный код подтверждения вызывает ValueError."""
        order = self.robot.create_order("Корпус B", "10:00–10:30")
        self.robot.accept_order(order)
        for _ in range(10000):
            self.robot.step()
            if not self.robot.state.busy:
                break
        with self.assertRaises(ValueError):
            self.robot.deliver("0000")

    def test_too_far_raises(self):
        """Если робот еще далеко, доставка невозможна."""
        order = self.robot.create_order("Корпус B", "10:00–10:30")
        self.robot.accept_order(order)
  
        with self.assertRaises(RuntimeError):
            self.robot.deliver("1234")


if __name__ == "__main__":
    unittest.main()
