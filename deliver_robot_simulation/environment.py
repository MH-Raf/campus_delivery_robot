import math
import matplotlib.pyplot as plt
from matplotlib.widgets import Button
import time
from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Tuple, Optional

CAMPUS_MAP = {
    "Корпус A": (7.0 * 100, 0 * 100),
    "Корпус B": (10.0 * 100, 5.0 * 100),
    "Общежитие": (2.0 * 100, 12.0 * 100),
    "Столовая": (7.0 * 100, 4.0 * 100),
    "Лабораторный корпус": (12.0 * 100, 3.0 * 100),
}

OBSTACLES = [
    (5 * 100, 5 * 100, 1.2 * 100),
    (8 * 100, 2 * 100, 1.0 * 100),
]