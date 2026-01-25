import time
class Simulation:
    def __init__(self, robot, visualizer):
        self.robot = robot
        self.visualizer = visualizer

    def run(self, steps=200, dt=0.1):
        for _ in range(steps):
            if not self.visualizer.paused:
                self.robot.step(dt)
            self.visualizer.draw()
            time.sleep(0.01)