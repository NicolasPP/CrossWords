from time import time
from typing import Optional


class DeltaTime:
    def __init__(self) -> None:
        self._prev_time: float = time()
        self._delta_time: Optional[float] = None

    def set(self) -> None:
        now: float = time()
        self._delta_time = now - self._prev_time
        self._prev_time = now

    def get(self) -> float:
        if self._delta_time is None:
            raise Exception("must set delta time before using it")
        return self._delta_time

    def get_fps(self) -> int:
        if self.get() == 0:
            return -1

        return round(1 / self.get())
