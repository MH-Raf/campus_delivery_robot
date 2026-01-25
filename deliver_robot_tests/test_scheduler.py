import unittest
from campus_deliver_robot import Scheduler, Order, CAMPUS_MAP


class TestScheduler(unittest.TestCase):

    def setUp(self):
        self.scheduler = Scheduler()

    def test_plan_valid(self):
        order = Order("Корпус B", "10:00–10:30", "123")
        pos = (0.0, 0.0)
        plan = self.scheduler.plan(pos, order)

        self.assertIn("route", plan)
        self.assertIn("eta", plan)
        self.assertIn("speed", plan)

        self.assertEqual(plan["route"][1], CAMPUS_MAP["Корпус B"])
        self.assertTrue(0.1 <= plan["speed"] <= 3.0)
        self.assertEqual(order.x, CAMPUS_MAP["Корпус B"][0])
        self.assertEqual(order.y, CAMPUS_MAP["Корпус B"][1])

    def test_invalid_address(self):
        order = Order("Неизвестный корпус", "10:00–10:30", "123")
        with self.assertRaises(ValueError):
            self.scheduler.plan((0, 0), order)


if __name__ == "__main__":
    unittest.main()
