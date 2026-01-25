import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist
from std_msgs.msg import String
from std_srvs.srv import Trigger

from .robot_adapter import RobotAdapter


class RobotNode(Node):
    def __init__(self):
        super().__init__("robot_node")

        self.declare_parameter("rate_hz", 50.0)
        rate = float(self.get_parameter("rate_hz").value)
        self.dt = 1.0 / rate

        self.adapter = RobotAdapter(self)

        self.sub_cmd = self.create_subscription(
            Twist, "cmd_vel", self.on_cmd, 10
        )

        self.pub_state = self.create_publisher(
            String, "state", 10
        )

        self.srv_a = self.create_service(Trigger, "run_a", self.on_run_a)
        self.srv_b = self.create_service(Trigger, "run_b", self.on_run_b)
        self.srv_stop = self.create_service(Trigger, "stop", self.on_stop)
        self.srv_reset = self.create_service(Trigger, "reset", self.on_reset)

        self.timer = self.create_timer(self.dt, self.on_tick)

    def on_cmd(self, msg: Twist):
        self.adapter.mode = "manual"
        self.adapter.apply_cmd_vel(msg)

    def on_tick(self):
        self.adapter.step(self.dt)
        msg = String()
        msg.data = self.adapter.status_text()
        self.pub_state.publish(msg)

    def on_run_a(self, req, res):
        res.success, res.message = self.adapter.run_a()
        return res

    def on_run_b(self, req, res):
        res.success, res.message = self.adapter.run_b()
        return res

    def on_stop(self, req, res):
        res.success, res.message = self.adapter.stop()
        return res

    def on_reset(self, req, res):
        res.success, res.message = self.adapter.reset()
        return res


def main():
    rclpy.init()
    node = RobotNode()

    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        if rclpy.ok():
            rclpy.shutdown()
