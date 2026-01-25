from fastapi import FastAPI, HTTPException, BackgroundTasks
from typing import List
from datetime import datetime
from robot_service import robot_service, RobotStatus
from models import (
    CreateOrderRequest, OrderResponse, DeliverOrderRequest,
    SensorResponse, ActuatorResponse, ScenarioRequest
)

app = FastAPI(title="Courier Robot API", version="1.0")

@app.post("/robot/init")
def init_robot():
    try:
        robot_service.initialize()
        return {"message": "Robot initialized successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/orders", response_model=OrderResponse)
def create_order(req: CreateOrderRequest):
    try:
        order = robot_service.create_order(req.address, req.delivery_window)
        return OrderResponse(
            address=order.address,
            delivery_window=order.delivery_window,
            confirmation_code=order.confirmation_code,
            status=order.status,
            eta=order.eta,
            delivered_at=order.delivered_at
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except RuntimeError as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/orders/{confirmation_code}/accept")
def accept_order(confirmation_code: str):
    order = robot_service.current_order

    if not order or order.confirmation_code != confirmation_code:
        raise HTTPException(status_code=404, detail="Order not found")

    try:
        plan = robot_service.robot.controller.accept_order(order)
        return plan
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/orders/{confirmation_code}/deliver")
def deliver_order(confirmation_code: str, req: DeliverOrderRequest):
    if not robot_service.current_order or robot_service.current_order.confirmation_code != confirmation_code:
        raise HTTPException(status_code=404, detail="Order not found")
    try:
        result = robot_service.deliver_order(req.confirmation_code)
        return result
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.get("/robot/sensors", response_model=SensorResponse)
def get_sensors():
    try:
        return {"data": robot_service.get_sensor_state()}
    except RuntimeError as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.get("/robot/actuators", response_model=ActuatorResponse)
def get_actuators():
    try:
        return {"data": robot_service.get_actuator_state()}
    except RuntimeError as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/robot/simulate-step")
def simulate_step(dt: float = 1.0):
    try:
        robot_service.robot.step(dt=dt)
        state = robot_service.robot.state
        return {
            "position": state.position,
            "speed": state.speed,
            "busy": state.busy
        }
    except RuntimeError as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.get("/robot/status")
def get_status():
    return robot_service.get_status()
