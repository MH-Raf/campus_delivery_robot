import time
import campus_delivery_robot as lr1
from robot_service_cached import CachedScheduler

robot = lr1.CourierRobot()

addresses = ["Корпус A", "Столовая", "Корпус B", "Общежитие"]


def benchmark():
    plain_scheduler = lr1.Scheduler()
    cached_scheduler = CachedScheduler(capacity=128, ttl_seconds=60)

    pos = (0.0, 0.0)
    order = lr1.Order("Корпус B", "10:00–10:30", "1234")

    # Обычный
    t0 = time.time()
    for _ in range(4000):
        plain_scheduler.plan(pos, order)
    t_plain = time.time() - t0

    # Кэшируемый
    t0 = time.time()
    for _ in range(4000):
        cached_scheduler.plan(pos, order)
    t_cached = time.time() - t0

    return {
        "plain_scheduler_time": t_plain,
        "cached_scheduler_time": t_cached,
        "speedup": t_plain / t_cached if t_cached > 0 else None,
        "cache_hits": cached_scheduler.hits,
        "cache_misses": cached_scheduler.misses,
    }


if __name__ == "__main__":
    print(benchmark())
