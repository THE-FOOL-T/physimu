"""Small local-server limits; no image or request bodies are logged."""

import asyncio
from collections import deque
import threading
import time
from fastapi.responses import JSONResponse


class RequestLimits:
    def __init__(self, app, max_bytes=21 * 1024 * 1024, timeout=30):
        self.app, self.max_bytes, self.timeout = app, max_bytes, timeout

    async def __call__(self, scope, receive, send):
        if scope["type"] != "http" or scope["method"] not in {"POST", "PUT", "PATCH"}:
            return await self.app(scope, receive, send)
        chunks = []
        size = 0
        try:
            async with asyncio.timeout(self.timeout):
                while True:
                    message = await receive()
                    if message["type"] == "http.disconnect":
                        return
                    size += len(message.get("body", b""))
                    if size > self.max_bytes:
                        response = JSONResponse(
                            status_code=413,
                            content={
                                "detail": {"code": "too_large", "message_key": "error.too_large"}
                            },
                        )
                        return await response(scope, receive, send)
                    chunks.append(message)
                    if not message.get("more_body", False):
                        break
        except TimeoutError:
            response = JSONResponse(
                status_code=408,
                content={"detail": {"code": "timeout", "message_key": "error.timeout"}},
            )
            return await response(scope, receive, send)
        messages = iter(chunks)

        async def replay():
            return next(messages, None) or await receive()

        await self.app(scope, replay, send)


class RateLimiter:
    def __init__(self, limit=120, seconds=60, clock=time.monotonic):
        self.limit, self.seconds, self.clock = limit, seconds, clock
        self.clients = {}
        self.lock = threading.Lock()

    def allow(self, client):
        with self.lock:
            now = self.clock()
            # Expire idle client entries as well as individual timestamps.
            self.clients = {
                key: values
                for key, values in self.clients.items()
                if values and values[-1] > now - self.seconds
            }
            values = self.clients.setdefault(client, deque())
            while values and values[0] <= now - self.seconds:
                values.popleft()
            if len(values) >= self.limit:
                return False
            values.append(now)
            return True
