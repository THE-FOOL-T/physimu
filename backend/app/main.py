"""Local API. Uploaded bytes live in memory; only opted-in corrections persist."""

import json
import logging
import time
import uuid
from contextlib import asynccontextmanager
from contextlib import suppress
import asyncio
from pathlib import Path
from typing import Any
import cv2
from fastapi import FastAPI, File, Form, UploadFile, HTTPException, Request
from fastapi.concurrency import run_in_threadpool
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.exceptions import RequestValidationError
from .limits import RequestLimits, RateLimiter
from .analysis import run_analysis
from ..domains.circuit.warnings import ordered
from pydantic import BaseModel, Field
from ..domains.circuit.netlist import Netlist
from ..core.preprocess import decode, MAX_BYTES
from ..domains.circuit.engine import analyze_page
from ..domains.circuit.resolve import resolve
from ..domains.circuit.validate import safe_solve, fallback, validate
from ..domains.circuit.solver.mna import transient
from ..core.config import load_config
from ..core.jobs import JobStore
from .warmup import state as model_state, start_warmup
from ..domains import get as get_domain, names as domain_names
from ..core.models import model_lease

ROOT = Path(__file__).resolve().parents[2]
log = logging.getLogger("circuit_sim")
log.setLevel(logging.INFO)
if not log.handlers:
    handler = logging.StreamHandler()
    handler.setFormatter(logging.Formatter("%(message)s"))
    log.addHandler(handler)
log.propagate = False


@asynccontextmanager
async def lifespan(app):
    with model_lease("circuit"):
        start_warmup()

    async def expire_jobs():
        while True:
            await asyncio.sleep(30)
            with jobs.lock:
                jobs.cleanup()

    expiration = asyncio.create_task(expire_jobs())
    try:
        yield
    finally:
        expiration.cancel()
        with suppress(asyncio.CancelledError):
            await expiration
        with jobs.lock:
            for id_, job in list(jobs.jobs.items()):
                if not job["finished"]:
                    jobs.cancel(id_)
        from ..core.ocr_hybrid.worker import close_workers

        close_workers()


app = FastAPI(title="Circuit Atelier", version="0.2.0", lifespan=lifespan)
cfg = load_config()["storage"]
app.add_middleware(RequestLimits)
limiter = RateLimiter(load_config()["storage"].get("job_requests_per_minute", 600))
jobs = JobStore(limit=cfg.get("max_jobs", 2), ttl=cfg.get("ttl_seconds", 900))


@app.middleware("http")
async def request_log(request: Request, call_next):
    id_ = uuid.uuid4().hex
    request.state.request_id = id_
    start = time.perf_counter()
    response = await call_next(request)
    response.headers["X-Request-ID"] = id_
    log.info(
        json.dumps(
            {
                "request_id": id_,
                "method": request.method,
                "path": request.url.path,
                "status": response.status_code,
                "seconds": round(time.perf_counter() - start, 4),
            }
        )
    )
    return response


class SolveRequest(BaseModel):
    netlist: Netlist
    overrides: dict[str, float] = Field(default_factory=dict)
    keep_constraints: bool = True
    transient: bool = False
    duration: float | None = Field(default=None, gt=0)
    steps: int | None = Field(default=None, ge=2, le=5000)
    state: dict[str, float] = Field(default_factory=dict)


@app.get("/api/domains")
def domains():
    return {
        "domains": [{"name": name, "stages": get_domain(name).stages} for name in domain_names()]
    }


@app.get("/api/health")
def health():
    readiness = dict(model_state)
    if readiness.get("ocr_backend") == "hybrid":
        from ..core.ocr_hybrid.worker import worker_states

        engines = worker_states()
        readiness["ocr_engines"] = engines
        if engines and readiness["ocr"] != "warming":
            readiness["ocr"] = (
                "ready"
                if len(engines) == 2 and all(s == "ready" for s in engines.values())
                else "warming"
                if "warming" in engines.values()
                else "unavailable"
            )
    return {
        "status": "ok",
        **readiness,
        "detector_available": Path(load_config()["detector"]["weights"]).is_file(),
        "storage": "memory_only_unless_corrections_opt_in",
        "version": 1,
    }


async def read_upload(image):
    data = await image.read(MAX_BYTES + 1)
    if len(data) > MAX_BYTES:
        raise HTTPException(413, detail={"code": "too_large"})
    return data


def check_rate(request):
    client = request.client.host if request.client else "local"
    if not limiter.allow(client):
        raise HTTPException(
            429, detail={"code": "rate_limited", "message_key": "error.rate_limited"}
        )


@app.exception_handler(HTTPException)
async def typed_http_error(request, exc):
    detail = exc.detail if isinstance(exc.detail, dict) else {"code": "invalid_request"}
    detail.setdefault("message_key", "error." + detail["code"])
    return JSONResponse(status_code=exc.status_code, content={"detail": detail})


@app.exception_handler(RequestValidationError)
async def typed_validation_error(request, exc):
    return JSONResponse(
        status_code=422,
        content={"detail": {"code": "invalid_request", "message_key": "error.invalid_request"}},
    )


@app.post("/api/analyze")
async def analyze(
    request: Request,
    image: UploadFile = File(...),
    problem_text: str | None = Form(None),
    lang: str = Form("en"),
    page: str = Form("0"),
    style: str = Form("auto"),
    use_label_reader: bool = Form(False),
    domain: str = Form("circuit"),
):
    started = await analyze_start(
        request, image, problem_text, lang, page, style, use_label_reader, domain
    )
    id_ = started["job_id"]
    try:
        async with asyncio.timeout(60):
            while True:
                job = jobs.get(id_)
                if job["error"]:
                    raise HTTPException(500, detail=job["error"])
                if job["result"] is not None:
                    result = job["result"]
                    jobs.cancel(id_)
                    return result
                await asyncio.sleep(0.01)
    except TimeoutError as exc:
        jobs.cancel(id_)
        raise HTTPException(408, detail={"code": "timeout"}) from exc


async def validated_image(image, data, page):
    suffix = Path(image.filename or "").suffix.lower()
    if suffix not in {".png", ".jpg", ".jpeg", ".webp", ".heic", ".heif", ".pdf"}:
        raise HTTPException(415, detail={"code": "unsupported_type"})
    try:
        page = int(page)
    except (TypeError, ValueError) as exc:
        raise HTTPException(422, detail={"code": "invalid_page"}) from exc
    if page < 0:
        raise HTTPException(422, detail={"code": "invalid_page"})
    try:
        return await run_in_threadpool(decode, data, page)
    except Exception as exc:
        code = (
            "invalid_page"
            if str(exc) == "invalid_page"
            else "too_large"
            if str(exc) in {"too_large", "too_many_pixels"}
            else "undecodable"
        )
        raise HTTPException(
            422 if code == "invalid_page" else 413 if code == "too_large" else 415,
            detail={"code": code},
        ) from exc


@app.post("/api/analyze/start")
async def analyze_start(
    request: Request,
    image: UploadFile = File(...),
    problem_text: str | None = Form(None),
    lang: str = Form("en"),
    page: str = Form("0"),
    style: str = Form("auto"),
    use_label_reader: bool = Form(False),
    domain: str = Form("circuit"),
):
    # FastAPI treats an empty optional form value as its default. It is still
    # an explicit, unknown domain, so validate the submitted value when present.
    domain = str((await request.form()).get("domain", domain))
    try:
        selected_domain = get_domain(domain)
    except KeyError as exc:
        raise HTTPException(400, detail={"code": "unknown_domain"}) from exc
    check_rate(request)
    data = await read_upload(image)
    decoded = await validated_image(image, data, page)
    try:
        id_ = jobs.start(
            lambda progress: run_analysis(
                decoded,
                problem_text,
                lang if lang in {"en", "bn"} else "en",
                style,
                progress=progress,
                use_label_reader=use_label_reader,
                request_id=request.state.request_id,
                domain=selected_domain,
            ),
            request_id=request.state.request_id,
            stages=selected_domain.stages,
        )
    except OverflowError as exc:
        raise HTTPException(429, detail={"code": "busy"}) from exc
    pages = 1
    if data.startswith(b"%PDF-"):
        import pypdfium2

        doc = pypdfium2.PdfDocument(data)
        try:
            pages = len(doc)
        finally:
            doc.close()
    return {
        "job_id": id_,
        "width": decoded.shape[1],
        "height": decoded.shape[0],
        "page_count": pages,
        "domain": selected_domain.name,
        "stages": selected_domain.stages,
    }


@app.get("/api/analyze/{job_id}")
def analysis_status(job_id: str, request: Request, include_image: bool = True):
    check_rate(request)
    try:
        return jobs.get(
            job_id,
            include_image=include_image and request.headers.get("x-include-image") != "false",
        )
    except KeyError as exc:
        raise HTTPException(404, detail={"code": "expired"}) from exc


@app.delete("/api/analyze/{job_id}")
def analysis_cancel(job_id: str):
    try:
        jobs.cancel(job_id)
    except KeyError as exc:
        raise HTTPException(404, detail={"code": "expired"}) from exc
    return {"cancelled": True}


def solve_request(body):
    net = body.netlist.model_copy(deep=True)
    net.image.path = ""
    for id_, value in body.overrides.items():
        c = next((c for c in net.components if c.id == id_), None)
        if c:
            c.value.number = value
            c.value.status = "user"
            c.value.source = "user"
            c.value.confidence = 1
    if body.keep_constraints:
        net = resolve(net)
    net = validate(net)
    net, result = safe_solve(net)
    result["warnings"] = ordered(result["warnings"])
    response = {"netlist": net.as_dict(), "solution": result}
    if body.transient:
        response["transient"] = transient(net, body.duration, body.steps, body.state or None)
    return response


@app.post("/api/solve")
def solve_api(body: SolveRequest):
    return solve_request(body)


@app.post("/api/resolve")
def resolve_api(body: SolveRequest):
    net = body.netlist.model_copy(deep=True)
    net.image.path = ""
    net = resolve(net, body.keep_constraints)
    return {"netlist": net.as_dict()}


@app.post("/api/corrections")
async def corrections(
    image: UploadFile = File(...),
    netlist: str | None = Form(None),
    opt_in: bool = Form(False),
    texts: str = Form("[]"),
    domain: str = Form("circuit"),
    scene: str | None = Form(None),
):
    if domain not in {"circuit", "mechanics"}:
        raise HTTPException(400, detail={"code": "unknown_domain"})
    if domain == "mechanics":
        if not opt_in:
            raise HTTPException(400, detail="Explicit correction storage opt-in required")
        from ..domains.mechanics.corrections import save_correction

        data = await read_upload(image)
        try:
            return await run_in_threadpool(save_correction, data, scene, ROOT)
        except ValueError as exc:
            raise HTTPException(422, detail={"code": "invalid_correction"}) from exc
    if netlist is None:
        raise HTTPException(422, detail={"code": "invalid_request"})
    if not opt_in:
        raise HTTPException(400, detail="Explicit correction storage opt-in required")
    data = await read_upload(image)
    try:
        net = Netlist.model_validate_json(netlist)
        if len(texts) > 65536:
            raise ValueError("Too much text correction data")
        text_labels = json.loads(texts)
        if not isinstance(text_labels, list) or len(text_labels) > 256:
            raise ValueError("Invalid text correction data")
        text_labels = [
            TextCorrection.model_validate(item).model_dump(mode="json") for item in text_labels
        ]
        decoded = await run_in_threadpool(decode, data)
    except Exception as exc:
        raise HTTPException(422, detail="Invalid corrected netlist or image") from exc
    # Persist the exact displayed (possibly perspective-corrected/cropped) raster embedded
    # in the netlist, so correction coordinates stay aligned with their training image.
    if net.image.path.startswith("data:image/png;base64,"):
        import base64

        try:
            decoded = await run_in_threadpool(
                decode, base64.b64decode(net.image.path.split(",", 1)[1], validate=True)
            )
        except Exception as exc:
            raise HTTPException(422, detail="Invalid netlist raster") from exc
    if (decoded.shape[1], decoded.shape[0]) != (net.image.width, net.image.height):
        raise HTTPException(422, detail="Image dimensions must match netlist coordinate space")
    id_ = uuid.uuid4().hex
    dest = ROOT / "data/corrections" / id_
    dest.mkdir(parents=True)
    net.image.path = "image.png"
    (dest / "netlist.json").write_text(
        json.dumps(net.as_dict(), ensure_ascii=False, indent=2), encoding="utf-8"
    )
    (dest / "texts.json").write_text(
        json.dumps(text_labels, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    cv2.imwrite(str(dest / "image.png"), decoded)
    (dest / "consent.json").write_text(json.dumps({"opt_in": True, "created_unix": time.time()}))
    return {"id": id_, "saved": True}


class TextCorrection(BaseModel):
    bbox: tuple[float, float, float, float]
    text: str = Field(max_length=1000)
    component_id: str | None = Field(default=None, max_length=100)
    ignored: bool = False


@app.post("/api/ocr-crop")
async def ocr_crop(
    image: UploadFile = File(...),
    component_type: str = Form("resistor"),
    use_label_reader: bool = Form(False),
):
    data = await read_upload(image)
    decoded = await validated_image(image, data, 0)
    if decoded.shape[1] > 640 or decoded.shape[0] > 256:
        raise HTTPException(
            413,
            detail={"code": "crop_too_large", "message_key": "error.crop_too_large"},
        )
    from ..core.text import read_text
    from ..domains.circuit.label_assignment import parse_item

    diagnostics = {}
    items, warnings = await run_in_threadpool(
        read_text, decoded, components=None, diagnostics=diagnostics
    )
    if use_label_reader:
        from ..core.ocr_label_reader import configured_reader, valid_label

        reader = configured_reader()
        if reader is None:
            warnings.append(("label_reader_unavailable", None))
        elif decoded.shape[0] <= 160:
            try:
                proposed = await run_in_threadpool(reader.read_labels, decoded)
                items.extend(
                    {
                        **item,
                        "source": "vlm",
                        "confidence": min(0.65, item.get("confidence", 0)),
                    }
                    for item in proposed
                    if valid_label(item.get("text", ""))
                )
            except Exception as exc:
                log.exception("Crop reader failed: %s", type(exc).__name__)
                warnings.append(("label_reader_failed", None))
    candidates = []
    for item in items:
        parsed = parse_item(item, component_type)
        if parsed:
            candidates.append({**item, "parsed": parsed})
    return {
        "candidates": candidates,
        "diagnostics": diagnostics,
        "warnings": [
            {"code": code, "ref": ref, "message_key": "warn." + code} for code, ref in warnings
        ],
    }


dist = ROOT / "frontend/dist"
if dist.is_dir():
    app.mount("/", StaticFiles(directory=dist, html=True), name="frontend")
