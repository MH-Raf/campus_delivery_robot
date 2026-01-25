import unittest
from campus_deliver_robot import PositionSensor, RobotState


class TestPositionSensor(unittest.TestCase):
    """Тесты для класса PositionSensor."""

    def setUp(self):
        """Создание робота с начальными координатами."""
        self.state = RobotState(position=(100.0, 200.0))
        self.sensor = PositionSensor(self.state)

    def tearDown(self):
        """Очистка после теста."""
        self.state = None
        self.sensor = None

    def test_read_initial_position(self):
        """Проверяем начальные координаты сенсора."""
        self.assertEqual(self.sensor.read(), (100.0, 200.0))

    def test_read_after_move(self):
        """Проверяем координаты после изменения позиции."""
        self.state.position = (300.0, 50.0)
        self.assertEqual(self.sensor.read(), (300.0, 50.0))

    def test_read_type(self):
        """Проверяем, что возвращается кортеж из двух float."""
        pos = self.sensor.read()
        self.assertIsInstance(pos, tuple)
        self.assertEqual(len(pos), 2)
        self.assertTrue(all(isinstance(v, float) for v in pos))

    def test_zero_position(self):
        """Граничный случай: координаты (0,0)."""
        self.state.position = (0.0, 0.0)
        self.assertEqual(self.sensor.read(), (0.0, 0.0))

    def test_negative_position(self):
        """Граничный случай: отрицательные координаты."""
        self.state.position = (-10.0, -20.0)
        self.assertEqual(self.sensor.read(), (-10.0, -20.0))


if __name__ == "__main__":
    unittest.main()
