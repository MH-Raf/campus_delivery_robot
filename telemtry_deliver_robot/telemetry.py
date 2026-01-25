import sqlite3
from datetime import datetime
from time import sleep
from random import random
from typing import Optional, Tuple
from dataclasses import dataclass
import os

@dataclass
class RobotState:
    position: Tuple[float, float] = (0.0, 0.0)
    speed: float = 1.0
    busy: bool = False

@dataclass
class Order:
    address: str
    confirmation_code: str
    status: str = "pending"

class PositionSensor:
    def __init__(self, state: RobotState):
        self._state = state
    def read(self) -> Tuple[float, float]:
        return self._state.position

class Drive:
    def __init__(self, state: RobotState):
        self._state = state
        self.target: Optional[Tuple[float, float]] = None
    def command(self, target: Tuple[float, float]):
        self.target = target
    def update(self):
        if not self.target:
            return
        x, y = self._state.position
        tx, ty = self.target
        dx, dy = tx - x, ty - y
        dist = (dx*dx + dy*dy)**0.5
        if dist < 0.01:
            self._state.position = self.target
            return
        step = 0.1
        self._state.position = (x + dx/dist*step, y + dy/dist*step)


class Controller:
    def __init__(self, sensor: PositionSensor, drive: Drive, state: RobotState):
        self.sensor = sensor
        self.drive = drive
        self.state = state
    def step(self) -> float:
        pos = self.sensor.read()
        target = (5.0, 5.0)
        self.drive.command(target)
        self.drive.update()
        return ((target[0]-pos[0])**2 + (target[1]-pos[1])**2)**0.5


class TelemetryLogger:
    def __init__(self, db_path: str = "robot_telemetry.db"):
        self.db_path = db_path
        self._conn: Optional[sqlite3.Connection] = None
        self.session_id: Optional[int] = None
    def connect(self):
        self._conn = sqlite3.connect(self.db_path)
        self._conn.execute("PRAGMA foreign_keys = ON;")
    def close(self):
        if self._conn: self._conn.close(); self._conn=None
    def init_schema(self):
        assert self._conn
        self._conn.executescript("""
        CREATE TABLE IF NOT EXISTS sessions (
          id INTEGER PRIMARY KEY, variant_id INTEGER NOT NULL,
          started_at TEXT NOT NULL, ended_at TEXT, status TEXT NOT NULL
        );
        CREATE TABLE IF NOT EXISTS sensor_readings (
          id INTEGER PRIMARY KEY AUTOINCREMENT,
          session_id INTEGER NOT NULL,
          sensor_type TEXT NOT NULL,
          timestamp TEXT NOT NULL,
          value REAL NOT NULL,
          unit TEXT,
          FOREIGN KEY(session_id) REFERENCES sessions(id) ON DELETE CASCADE
        );

        CREATE TABLE IF NOT EXISTS actuator_commands (
            id INTEGER PRIMARY KEY AUTOINCREMENT, session_id INTEGER NOT NULL,
            actuator_type TEXT NOT NULL, timestamp TEXT NOT NULL, command REAL NOT NULL, status TEXT,
            FOREIGN KEY(session_id) REFERENCES sessions(id) ON DELETE CASCADE
        
        );
        CREATE TABLE IF NOT EXISTS events (
          id INTEGER PRIMARY KEY AUTOINCREMENT, session_id INTEGER NOT NULL,
          timestamp TEXT NOT NULL, event_type TEXT NOT NULL, severity TEXT NOT NULL,
          message TEXT NOT NULL,
          FOREIGN KEY(session_id) REFERENCES sessions(id) ON DELETE CASCADE
        );
        """)
        self._conn.commit()
    def start_session(self, variant_id: int) -> int:
        assert self._conn
        ts = datetime.utcnow().isoformat()
        cur = self._conn.execute(
            "INSERT INTO sessions(variant_id, started_at, status) VALUES (?,?,?)",
            (variant_id, ts, "running")
        )
        self._conn.commit()
        self.session_id = cur.lastrowid
        return self.session_id
    def end_session(self, status: str = "completed"):
        assert self._conn and self.session_id
        ts = datetime.utcnow().isoformat()
        self._conn.execute(
            "UPDATE sessions SET ended_at=?, status=? WHERE id=?",
            (ts, status, self.session_id)
        )
        self._conn.commit()
    def log_sensor(self, sensor_type: str, value: float, unit: str=""):
        assert self._conn and self.session_id
        ts = datetime.utcnow().isoformat()
        self._conn.execute(
            "INSERT INTO sensor_readings(session_id, sensor_type, timestamp, value, unit) VALUES (?,?,?,?,?)",
            (self.session_id, sensor_type, ts, value, unit)
        )
        self._conn.commit()
    def log_command(self, actuator_type: str, command: float, status: str="sent"):
        assert self._conn and self.session_id
        ts = datetime.utcnow().isoformat()
        self._conn.execute(
            "INSERT INTO actuator_commands(session_id, actuator_type, timestamp, command, status) VALUES (?,?,?,?,?)",
            (self.session_id, actuator_type, ts, command, status)
        )
        self._conn.commit()
    def log_event(self, event_type: str, severity: str, message: str):
        assert self._conn and self.session_id
        ts = datetime.utcnow().isoformat()
        self._conn.execute(
            "INSERT INTO events(session_id, timestamp, event_type, severity, message) VALUES (?,?,?,?,?)",
            (self.session_id, ts, event_type, severity, message)
        )
        self._conn.commit()


logger = TelemetryLogger()
logger.connect()
logger.init_schema()
session_id = logger.start_session(variant_id=1)

robot_state = RobotState()
sensor = PositionSensor(robot_state)
drive = Drive(robot_state)
controller = Controller(sensor, drive, robot_state)

try:
    for step in range(50):
        # 1) Чтение сенсора
        pos = sensor.read()
        logger.log_sensor("position", pos[0], "x")
        logger.log_sensor("position", pos[1], "y")
        # 2) Команда
        cmd = controller.step()
        logger.log_command("drive_speed", cmd)
        # 3) События случайно
        if random() < 0.05:
            logger.log_event("noise", "warning", "Random noise spike detected")
        sleep(0.01)
    logger.end_session("completed")
except Exception as e:
    logger.log_event("exception", "error", str(e))
    logger.end_session("error")
finally:
    logger.close()

print("Сценарий выполнен. Данные записаны в robot_telemetry.db")
print(os.path.abspath("robot_telemetry.db"))