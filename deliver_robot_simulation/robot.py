import math
from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Tuple, Optional
from environment import CAMPUS_MAP, OBSTACLES
from physics import PhysicsEngine  # Предполагаем, что PhysicsEngine будет таким, как ниже
import time
@dataclass
class RobotState:
    position: Tuple[float, float] = (0.0, 0.0)
    speed: float = 1.0  # m/s
    speed_units: str = "м/с"
    busy: bool = False

@dataclass
class Order:
    address: str
    delivery_window: str
    confirmation_code: str
    status: str = "pending"
    eta: Optional[datetime] = None
    delivered_at: Optional[datetime] = None

class PositionSensor:
    def __init__(self, state): self.state = state
    def read(self): return self.state.position

class Scheduler:
    def plan(self, position, order):
        dest = CAMPUS_MAP[order.address]
        start, end = order.delivery_window.split("–")
        today = datetime.now().date()
        t_start = datetime.strptime(start, "%H:%M").replace(year=today.year, month=today.month, day=today.day)
        midpoint = t_start + (datetime.strptime(end, "%H:%M") - datetime.strptime(start, "%H:%M")) / 2

        dist = math.dist(position, dest)
        secs_to_mid = (midpoint - datetime.now()).total_seconds()

        # Speed in m/s (was km/h)
        if secs_to_mid <= 1:
            speed = 3.0
        else:
            speed = max(0.5, min(3.0, dist / secs_to_mid))

        eta = datetime.now() + timedelta(seconds=dist / speed)
        order.eta = eta
        return {"route": [position, dest], "eta": eta, "speed": speed}

class Controller:
    def __init__(self, sensor, scheduler, physics, state):
        self.sensor = sensor
        self.scheduler = scheduler
        self.physics = physics
        self.state = state

    def accept_order(self, order):
        pos = self.sensor.read()
        plan = self.scheduler.plan(pos, order)
        self.state.speed = plan["speed"]
        self.physics.set_target(plan["route"][-1])
        self.state.busy = True
        return plan

    def tick(self, dt): self.physics.step(dt)

class CourierRobot:
    def __init__(self, obstacles=OBSTACLES):
        self.state = RobotState()
        self.sensor = PositionSensor(self.state)
        self.physics = PhysicsEngine(self.state, obstacles)
        self.scheduler = Scheduler()
        self.controller = Controller(self.sensor, self.scheduler, self.physics, self.state)
        self.current_order = None
        self.speed_log = []
        self.distance_log = []
        self.time_log = []
        self.start_time = time.time()
        self.task_queue = []
        self.current_target = None

    def create_order(self, address, window):
        self.current_order = Order(address, window, confirmation_code="1234")
        return self.current_order

    def accept_order(self, order): return self.controller.accept_order(order)

    def step(self, dt):
        self.controller.tick(dt)
        if self.current_order and self.state.busy:
            tx, ty = CAMPUS_MAP[self.current_order.address]
            x, y = self.state.position
            if math.dist((x, y), (tx, ty)) < 5:
                self.state.speed = 0
                self.state.busy = False
                self.current_order.status = "delivered"
                self.current_order.delivered_at = datetime.now()
                self.state.position = (tx, ty)
                print(f"Robot reached destination: {self.current_order.address}")
        t = time.time() - self.start_time
        self.time_log.append(t)
        self.speed_log.append(self.state.speed)
        self.distance_log.append(self.physics.distance_travelled)

    def add_task(self, point):
        self.task_queue.append(point)
    def next_task(self):
        if self.task_queue:
            self.current_target = self.task_queue.pop(0)
        else:
            self.current_target = None


