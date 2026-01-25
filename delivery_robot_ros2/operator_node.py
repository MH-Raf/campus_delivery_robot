from __future__ import annotations

import math
from typing import Optional

import rclpy
from geometry_msgs.msg import Twist
from rclpy.node import Node
from std_srvs.srv import Trigger


class OperatorNode(Node):
    def __init__(self) -> None:
        super().__init__("operator_node")

        self.declare_parameter("namespace", "demo")
        self.declare_parameter("autostart", "a")  # a|b|none
        self.declare_parameter("start_delay_sec", 1.0)
        self.declare_parameter("stop_after_sec", 0.0)

        self.declare_parameter("manual_demo", False)
        self.declare_parameter("cmd_rate_hz", 10.0)
        self.declare_parameter("manual_linear", 0.2)
        self.declare_parameter("manual_angular", 0.8)
        self.declare_parameter("manual_duration_sec", 10.0)

        ns = str(self.get_parameter("namespace").value).strip("/")
        self._ns = ns if ns else "demo"

        self._pub_cmd = self.create_publisher(Twist, f"/{self._ns}/cmd_vel", 10)

        self._cli_run_a = self.create_client(Trigger, f"/{self._ns}/run_a")
        self._cli_run_b = self.create_client(Trigger, f"/{self._ns}/run_b")
        self._cli_stop = self.create_client(Trigger, f"/{self._ns}/stop")

        self._start_timer = self.create_timer(
            float(self.get_parameter("start_delay_sec").value), self._on_start
        )
        self._stop_timer: Optional[rclpy.timer.Timer] = None

        self._manual_timer: Optional[rclpy.timer.Timer] = None
        self._manual_t0_sec: Optional[float] = None

        self.get_logger().info(
            f"OperatorNode started: ns=/{self._ns}, autostart={self.get_parameter('autostart').value}"
        )

    def _now_sec(self) -> float:
        return self.get_clock().now().nanoseconds / 1e9

    def _call_trigger(self, client: rclpy.client.Client, label: str) -> None:
        if not client.wait_for_service(timeout_sec=2.0):
            self.get_logger().error(f"Service not available: {client.srv_name} ({label})")
            return

        future = client.call_async(Trigger.Request())

        def _done(fut: rclpy.task.Future) -> None:
            try:
                res = fut.result()
                self.get_logger().info(f"{label}: success={res.success}; message={res.message}")
            except Exception as e:  # noqa: BLE001
                self.get_logger().error(f"{label}: call failed: {e}")

        future.add_done_callback(_done)

    def _on_start(self) -> None:
        self._start_timer.cancel()

        autostart = str(self.get_parameter("autostart").value).strip().lower()
        if autostart == "a":
            self._call_trigger(self._cli_run_a, "run_a")
        elif autostart == "b":
            self._call_trigger(self._cli_run_b, "run_b")
        else:
            self.get_logger().info("autostart=none: scenario is not started")

        stop_after = float(self.get_parameter("stop_after_sec").value)
        if stop_after > 0.0:
            self._stop_timer = self.create_timer(stop_after, self._on_stop_timer)

        if bool(self.get_parameter("manual_demo").value):
            rate_hz = max(1.0, float(self.get_parameter("cmd_rate_hz").value))
            self._manual_t0_sec = self._now_sec()
            self._manual_timer = self.create_timer(1.0 / rate_hz, self._manual_tick)

    def _on_stop_timer(self) -> None:
        if self._stop_timer is not None:
            self._stop_timer.cancel()
        self._call_trigger(self._cli_stop, "stop")

    def _manual_tick(self) -> None:
        if self._manual_t0_sec is None:
            return

        elapsed = self._now_sec() - self._manual_t0_sec
        duration = float(self.get_parameter("manual_duration_sec").value)
        if elapsed >= duration:
            if self._manual_timer is not None:
                self._manual_timer.cancel()
            msg = Twist()
            self._pub_cmd.publish(msg)
            return

        linear = float(self.get_parameter("manual_linear").value)
        angular = float(self.get_parameter("manual_angular").value)

        msg = Twist()
        msg.linear.x = linear
        msg.angular.z = angular * math.sin(elapsed * 0.7)
        self._pub_cmd.publish(msg)


def main(args: Optional[list[str]] = None) -> None:
    rclpy.init(args=args)
    node = OperatorNode()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()

