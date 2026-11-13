"""Cooperative page/stage deadlines; a native model call finishes atomically."""

import time
from .config import load_config


class BudgetExpired(BaseException):
    """Separate from reader failures and cooperative job cancellation."""


class Budget:
    def __init__(self, seconds=None, clock=time.monotonic):
        config = load_config().get("analysis", {})
        self.clock = clock
        self.end = clock() + (config.get("budget_seconds", 25) if seconds is None else seconds)
        self.stages = config.get("stage_seconds", {})
        self.deadlines = {}
        self.exceeded = set()

    def deadline(self, stage, reserve=0):
        if stage not in self.deadlines:
            self.deadlines[stage] = min(
                self.end - max(0, reserve), self.clock() + self.stages.get(stage, 25)
            )
        return self.deadlines[stage]

    def available(self, stage):
        available = self.clock() < self.deadline(stage)
        if not available:
            self.exceeded.add(stage)
        return available

    def check(self, stage):
        if not self.available(stage):
            raise BudgetExpired(stage)
