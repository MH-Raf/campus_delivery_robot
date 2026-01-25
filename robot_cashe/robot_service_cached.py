from collections import OrderedDict
from datetime import datetime, timedelta
from typing import Any, Dict, Tuple
import campus_delivery_robot as lr1


class LRUCacheTTL:
    def __init__(self, capacity: int = 128, ttl_seconds: int = 60):
        self.capacity = capacity
        self.ttl = timedelta(seconds=ttl_seconds)
        self.cache: OrderedDict[Tuple, Dict] = OrderedDict()

    def _is_expired(self, entry: Dict) -> bool:
        return datetime.now() > entry["timestamp"] + self.ttl

    def get(self, key: Tuple) -> Any:
        if key not in self.cache:
            return None
        entry = self.cache[key]
        if self._is_expired(entry):
            del self.cache[key]
            return None
        
        self.cache.move_to_end(key)
        return entry["value"]

    def put(self, key: Tuple, value: Any) -> None:
        
        self.cache[key] = {
            "value": value,
            "timestamp": datetime.now()
        }
        self.cache.move_to_end(key)

        if len(self.cache) > self.capacity:
            self.cache.popitem(last=False)



class CachedScheduler:
    def __init__(self, capacity: int = 128, ttl_seconds: int = 60):
        self._scheduler = lr1.Scheduler()
        self._cache = LRUCacheTTL(capacity, ttl_seconds)
        self.hits = 0
        self.misses = 0

    def plan(self, position: Tuple[float, float], order: lr1.Order) -> Dict:
        """
        Кэшируем только детерминированные данные:
        - route
        - speed
        - speed_units
        ETA пересчитываем каждый раз заново.
        """
        key = (position, order.address, order.delivery_window)

        cached = self._cache.get(key)
        if cached:
            self.hits += 1
            return {
                "route": cached["route"],
                "speed": cached["speed"],
                "speed_units": cached["speed_units"],
                "eta": datetime.now() + cached["route_eta"]
            }

        self.misses += 1
        plan = self._scheduler.plan(position, order)

        cached_plan = {
            "route": plan["route"],
            "speed": plan["speed"],
            "speed_units": plan["speed_units"],
            "route_eta": plan["eta"] - datetime.now()
        }
        self._cache.put(key, cached_plan)
        return plan
