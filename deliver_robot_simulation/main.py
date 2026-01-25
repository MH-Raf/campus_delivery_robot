from visualizer import Visualizer
from simulation import Simulation
from robot import CourierRobot
from environment import OBSTACLES

if __name__ == "__main__":
    robot = CourierRobot()
    order = robot.create_order("Корпус B", "10:00–10:30")
    robot.accept_order(order)
    vis = Visualizer(robot, OBSTACLES)
    sim = Simulation(robot, vis)
    sim.run(steps=1500, dt=10)