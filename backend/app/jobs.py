"""Bounded, memory-only, cooperative analysis jobs. No upload persistence."""

from concurrent.futures import ThreadPoolExecutor
import logging
import threading
import time
import uuid

STAGES = (
    "received",
    "preprocess",
    "detect",
    "text",
    "wires",
    "validate",
    "resolve",
    "solve",
    "done",
)
log = logging.getLogger("circuit_sim.jobs")


class Cancelled(BaseException):
    pass


class JobStore:
    def __init__(self, limit=2, ttl=900, max_retained=32):
        self.limit, self.ttl, self.max_retained = limit, ttl, max_retained
        self.executor = ThreadPoolExecutor(max_workers=limit, thread_name_prefix="analysis")
        self.jobs = {}
        self.active = 0
        self.lock = threading.RLock()

    def cleanup(self):
        now = time.monotonic()
        for id_, job in list(self.jobs.items()):
            if now - job["updated"] > self.ttl:
                self.cancel(id_)
                del self.jobs[id_]

    def _release(self, job):
        if job["counted"]:
            self.active -= 1
            job["counted"] = False

    def start(self, runner, request_id=None):
        with self.lock:
            self.cleanup()
            if self.active >= self.limit:
                raise OverflowError("busy")
            if len(self.jobs) >= self.max_retained:
                completed = [k for k, v in self.jobs.items() if v["finished"]]
                if not completed:
                    raise OverflowError("busy")
                del self.jobs[completed[0]]
            id_ = uuid.uuid4().hex
            now = time.monotonic()
            job = dict(
                stage="queued",
                started=now,
                updated=now,
                stage_started=now,
                partial={},
                result=None,
                error=None,
                cancel=threading.Event(),
                finished=False,
                counted=True,
                timings={},
                history=["queued"],
                runner=runner,
            )
            self.jobs[id_] = job
            self.active += 1

        def progress(stage, partial=None):
            with self.lock:
                if job["cancel"].is_set():
                    raise Cancelled()
                now = time.monotonic()
                previous = job["stage"]
                if stage != previous:
                    job["timings"][previous] = (
                        job["timings"].get(previous, 0) + now - job["stage_started"]
                    )
                    job["stage_started"] = now
                    job["history"].append(stage)
                job["stage"] = stage
                job["updated"] = now
                if partial:
                    job["partial"].update(partial)

        def work():
            try:
                progress("received")
                runner_ref = job.pop("runner", None)
                if runner_ref is None:
                    raise Cancelled()
                result = runner_ref(progress)
                progress("done")
                with self.lock:
                    if not job["cancel"].is_set():
                        job["result"] = result
            except Cancelled:
                with self.lock:
                    job["error"] = {"code": "cancelled", "message_key": "error.cancelled"}
            except Exception as exc:
                log.exception(
                    "Analysis server_error request_id=%s job_id=%s error_type=%s",
                    request_id or id_,
                    id_,
                    type(exc).__name__,
                )
                with self.lock:
                    job["error"] = {
                        "code": "server_error",
                        "message_key": "error.server_error",
                        "request_id": request_id or id_,
                    }
            finally:
                with self.lock:
                    job["finished"] = True
                    job["updated"] = time.monotonic()
                    self._release(job)

        with self.lock:
            job["future"] = self.executor.submit(work)
        return id_

    def get(self, id_, include_image=True):
        with self.lock:
            self.cleanup()
            job = self.jobs[id_]
            index = STAGES.index(job["stage"]) if job["stage"] in STAGES else 0
            partial = dict(job["partial"])
            if not include_image:
                partial.pop("source_image", None)
            if job["finished"]:
                partial = {}
            return dict(
                stage=job["stage"],
                stage_index=index,
                stage_count=len(STAGES),
                percent=round(100 * index / (len(STAGES) - 1)),
                elapsed_seconds=round(
                    (job["updated"] if job["finished"] else time.monotonic()) - job["started"],
                    3,
                ),
                partial=partial,
                result=job["result"],
                error=job["error"],
                stage_timings=dict(job["timings"]),
                history=list(job["history"]),
            )

    def cancel(self, id_):
        with self.lock:
            job = self.jobs[id_]
            job["cancel"].set()
            job["error"] = {"code": "cancelled", "message_key": "error.cancelled"}
            job["partial"] = {}
            job["result"] = None
            job["runner"] = None
            job["finished"] = True
            job["updated"] = time.monotonic()
            self._release(job)
            if job.get("future"):
                job["future"].cancel()
