import unittest
from campus_deliver_robot import Drive, RobotState


class TestDrive(unittest.TestCase):
    """Тесты для класса Drive."""

    def setUp(self):
        self.state = RobotState(position=(0.0, 0.0))
        self.drive = Drive(self.state)

    def tearDown(self):
        self.state = None
        self.drive = None

    def test_command_valid(self):
        """Команда с правильными координатами задается корректно."""
        self.drive.command((100.0, 200.0), speed=1.0)
        self.assertEqual(self.drive.target, (100.0, 200.0))
        self.assertEqual(self.drive.speed, 1.0)

    def test_command_invalid_type(self):
        """Команда с некорректным типом вызывает ошибку."""
        with self.assertRaises(ValueError):
            self.drive.command("abc", speed=1.0)
        with self.assertRaises(ValueError):
            self.drive.command((10.0,), speed=1.0)

    def test_update_moves_toward_target(self):
        """Робот сдвигается к цели после одного обновления."""
        self.drive.command((10.0, 0.0), speed=1.0)
        before = self.state.position[0]
        self.drive.update(dt=1.0)
        after = self.state.position[0]
        self.assertGreater(after, before)

    def test_update_reaches_target(self):
        """Робот достигает цели, если она близко (<0.1м)."""
        self.drive.command((0.05, 0.05), speed=1.0)
        for _ in range(10):
            self.drive.update(dt=1.0)
        self.assertEqual(self.state.position, self.drive.target)

    def test_update_no_target(self):
        """Если цель не задана, позиция не изменяется."""
        before = self.state.position
        self.drive.update(dt=1.0)
        self.assertEqual(self.state.position, before)


if __name__ == "__main__":
    unittest.main()
