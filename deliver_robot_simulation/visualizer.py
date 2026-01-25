import time
import math
import matplotlib.pyplot as plt
from matplotlib.widgets import Button
from environment import CAMPUS_MAP

class Visualizer:
    def __init__(self, robot, obstacles):
        self.robot = robot
        self.obstacles = obstacles
        self.paused = False
        self.traj_main_x = []
        self.traj_main_y = []
        self.traj_avoid_x = []
        self.traj_avoid_y = []


        self.fig, (self.ax_map, self.ax_telemetry) = plt.subplots(1, 2, figsize=(14, 6))
        plt.subplots_adjust(bottom=0.2)
        self.pause_button = Button(plt.axes([0.45, 0.05, 0.1, 0.075]), "Пауза/Пуск")
        self.pause_button.on_clicked(self.toggle)

    def toggle(self, _): self.paused = not self.paused

    def draw(self):
        
        self.ax_map.clear()
        for name, (x, y) in CAMPUS_MAP.items():
            self.ax_map.scatter(x, y, color='blue')
            self.ax_map.text(x+10, y+10, name)
        for ox, oy, r in self.obstacles:
            c = plt.Circle((ox, oy), r, color='red', alpha=0.3)
            self.ax_map.add_patch(c)
        rx, ry = self.robot.state.position
        if self.robot.physics.is_avoiding:
             self.traj_avoid_x.append(rx)
             self.traj_avoid_y.append(ry)
        else:
             self.traj_main_x.append(rx)
             self.traj_main_y.append(ry)
        self.ax_map.plot(self.traj_main_x, self.traj_main_y, color='blue', linestyle='--', label="Основной путь")
        self.ax_map.plot(self.traj_avoid_x, self.traj_avoid_y, color='orange', linestyle='--', label="Обход")
        self.ax_map.scatter(rx, ry, color='green')
        self.ax_map.set_title("Robot Simulation")
        self.ax_map.set_xlim(0, 1500)
        self.ax_map.set_ylim(0, 1500)

        self.ax_telemetry.clear()
        self.ax_telemetry.plot(self.robot.time_log, self.robot.speed_log, label="Скорость (м/с)")
        self.ax_telemetry.plot(self.robot.time_log, self.robot.distance_log, label="Дистанция (м)")
        self.ax_telemetry.set_xlabel("Время (с)")
        self.ax_telemetry.set_title("Телеметрия")
        self.ax_telemetry.legend()

        plt.pause(0.01)