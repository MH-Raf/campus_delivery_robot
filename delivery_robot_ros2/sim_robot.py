from __future__ import annotations

import math
from dataclasses import dataclass


def clamp(value: float, low: float, high: float) -> float:
    return max(low, min(high, value))


def normalize_angle(angle_rad: float) -> float:
    angle_rad = (angle_rad + math.pi) % (2.0 * math.pi) - math.pi
    return angle_rad


@dataclass(slots=True)
class Pose2D:
    x: float = 0.0
    y: float = 0.0
    yaw: float = 0.0  # radians


@dataclass(slots=True)
class Twist2D:
    v: float = 0.0  # m/s
    omega: float = 0.0  # rad/s


class SimRobot:
    def __init__(self, *, max_linear_speed: float, max_angular_speed: float) -> None:
        self.pose = Pose2D()
        self.cmd = Twist2D()
        self.max_linear_speed = float(max_linear_speed)
        self.max_angular_speed = float(max_angular_speed)

    def set_command(self, *, v: float, omega: float) -> None:
        self.cmd.v = clamp(float(v), -self.max_linear_speed, self.max_linear_speed)
        self.cmd.omega = clamp(float(omega), -self.max_angular_speed, self.max_angular_speed)

    def update(self, dt_sec: float) -> None:
        dt_sec = float(dt_sec)
        if dt_sec <= 0.0:
            return

        self.pose.yaw = normalize_angle(self.pose.yaw + self.cmd.omega * dt_sec)
        self.pose.x += self.cmd.v * math.cos(self.pose.yaw) * dt_sec
        self.pose.y += self.cmd.v * math.sin(self.pose.yaw) * dt_sec

    def reset(self) -> None:
        self.pose = Pose2D()
        self.cmd = Twist2D()

    def status_text(self) -> str:
        return (
            f"x={self.pose.x:.2f}, y={self.pose.y:.2f}, yaw={self.pose.yaw:.2f} rad; "
            f"v={self.cmd.v:.2f} m/s, omega={self.cmd.omega:.2f} rad/s"
        )

