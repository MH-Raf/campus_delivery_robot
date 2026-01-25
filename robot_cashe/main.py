from fastapi import FastAPI
from pydantic import BaseModel
from typing import Tuple
from datetime import datetime
import campus_delivery_robot as lr1
from robot_service_cached import CachedScheduler

app = FastAPI(title="Robot caching API")

robot = lr1.CourierRobot()

scheduler = CachedScheduler(capacity=128, ttl_seconds=60)


class OrderRequest(BaseModel):
    address: str
    window: str


class TelemetryResponse(BaseModel):
    x: float
    y: float
    busy: bool
    speed: float
    speed_units: str
    time: str


@app.post("/order/")
def create_order(req: OrderRequest):
    order = robot.create_order(req.address, req.window)

    pos = robot.sensor.read()
    plan = scheduler.plan(pos, order)

    robot.state.speed = plan["speed"]
    robot.state.speed_units = plan["speed_units"]
    robot.controller.drive.command(plan["route"][-1])
    robot.state.busy = True

    return {
        "route": plan["route"],
        "eta": plan["eta"].strftime("%H:%M:%S"),
        "speed": plan["speed"],
        "speed_units": plan["speed_units"],
        "cache_hits": scheduler.hits,
        "cache_misses": scheduler.misses,
    }


@app.get("/telemetry/")
def telemetry():
    x, y = robot.state.position
    return TelemetryResponse(
        x=x,
        y=y,
        busy=robot.state.busy,
        speed=robot.state.speed,
        speed_units=robot.state.speed_units,
        time=datetime.now().strftime("%H:%M:%S"),
    )


@app.post("/step/")
def step():
    robot.step()
    return {"status": "ok"}
