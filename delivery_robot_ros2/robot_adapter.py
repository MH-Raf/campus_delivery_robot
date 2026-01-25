from geometry_msgs.msg import Twist
from .sim_robot import SimRobot


class RobotAdapter:
    def __init__(self, node):
        self.node = node

        self.robot = SimRobot(
            max_linear_speed=node.declare_parameter("max_linear_speed", 0.5).value,
            max_angular_speed=node.declare_parameter("max_angular_speed", 1.5).value,
        )

        self.mode = "idle"  # idle | a | b | manual

    # ===== вход из /cmd_vel =====
    def apply_cmd_vel(self, msg: Twist):
        if self.mode == "manual":
            self.robot.set_command(
                v=msg.linear.x,
                omega=msg.angular.z,
            )

    # ===== сценарии =====
    def run_a(self):
        self.mode = "a"
        return True, "Scenario A: forward motion"

    def run_b(self):
        self.mode = "b"
        return True, "Scenario B: rotation"

    def stop(self):
        self.mode = "idle"
        self.robot.set_command(v=0.0, omega=0.0)
        return True, "Stopped"

    def reset(self):
        self.robot.reset()
        return True, "Reset"

    # ===== основной шаг =====
    def step(self, dt: float):
        if self.mode == "a":
            self.robot.set_command(v=0.2, omega=0.0)
        elif self.mode == "b":
            self.robot.set_command(v=0.0, omega=0.6)

        self.robot.update(dt)

    def status_text(self) -> str:
        return self.robot.status_text()
