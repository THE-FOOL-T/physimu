"""Verification-only Python guard: local IPC/loopback allowed, external IP denied."""

import json
import os
import sys

LOCAL = {"127.0.0.1", "::1", "localhost", "localhost.localdomain"}


def guard(event, args):
    host = None
    if event == "socket.connect" and isinstance(args[1], tuple):
        host = args[1][0]
    elif event == "socket.getaddrinfo":
        host = args[0]
    if host is None or str(host).lower() in LOCAL:
        return
    destination = os.environ.get("AUGPHYS_OFFLINE_LOG")
    if destination:
        with open(destination, "a", encoding="utf-8") as stream:
            stream.write(
                json.dumps({"runtime": "python", "event": event, "host": str(host)}) + "\n"
            )
    raise PermissionError("M0 verification blocks external network access")


if os.environ.get("AUGPHYS_OFFLINE") == "1":
    sys.addaudithook(guard)
