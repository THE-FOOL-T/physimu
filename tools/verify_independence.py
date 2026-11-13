"""Reproduce M0 with the origin absent and external-network guards enabled."""

import argparse
import json
import os
from pathlib import Path
import subprocess
import sys
import time
import urllib.request
import uuid

ROOT = Path(__file__).resolve().parents[1]
CACHE = ROOT / ".cache/m0-isolation"


def run(command, name, env, timeout=600, cwd=ROOT):
    print(f"Running {name}", flush=True)
    with (CACHE / f"{name}.log").open("w", encoding="utf-8") as output:
        result = subprocess.run(
            command,
            cwd=cwd,
            env=env,
            stdout=output,
            stderr=subprocess.STDOUT,
            timeout=timeout,
            creationflags=subprocess.CREATE_NO_WINDOW if os.name == "nt" else 0,
        )
    if result.returncode:
        raise RuntimeError(f"{name} failed ({result.returncode}); see {CACHE / (name + '.log')}")


def http_json(path, data=None, headers=None):
    request = urllib.request.Request(
        "http://127.0.0.1:8000" + path, data=data, headers=headers or {}
    )
    with urllib.request.urlopen(request, timeout=60) as response:
        return json.load(response)


def main():
    global CACHE
    parser = argparse.ArgumentParser()
    parser.add_argument("--source", required=True, type=Path)
    parser.add_argument("--browser", action="store_true")
    parser.add_argument("--browser-only", action="store_true")
    parser.add_argument("--browser-filter")
    parser.add_argument("--browser-repeat", type=int, default=1)
    parser.add_argument("--out", type=Path, default=CACHE)
    args = parser.parse_args()
    CACHE = args.out.resolve()
    if not CACHE.is_relative_to(ROOT / ".cache"):
        parser.error("Verification logs must stay inside this workspace's .cache")
    if args.browser_only and not args.browser:
        parser.error("--browser-only requires --browser")
    if not 1 <= args.browser_repeat <= 10:
        parser.error("Browser repetition must be between 1 and 10")
    source = args.source.resolve(strict=True)
    manifest = json.loads((ROOT / "docs/import-manifest.json").read_text(encoding="utf-8"))
    if source == ROOT or source.is_relative_to(ROOT) or ROOT.is_relative_to(source):
        parser.error("Source must be a separate, explicitly selected checkout")
    commit = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=source).decode().strip()
    if commit != manifest["commit"]:
        parser.error("Source commit differs from the imported baseline")
    if subprocess.check_output(["git", "status", "--porcelain"], cwd=source).strip():
        parser.error("Source must be clean before the temporary isolation rename")
    hidden = source.with_name(source.name + ".m0-absent-" + uuid.uuid4().hex)
    # Verify both absolute move targets remain inside the explicitly selected parent.
    if (
        hidden.parent != source.parent
        or not hidden.is_relative_to(source.parent)
        or hidden.exists()
    ):
        parser.error("Invalid temporary source target")
    CACHE.mkdir(parents=True, exist_ok=True)
    env = {key: value for key, value in os.environ.items() if not key.startswith("CIRCUIT_")}
    guard = ROOT / "tools/offline"
    env.update(
        AUGPHYS_OFFLINE="1",
        YOLO_OFFLINE="true",
        PYTHONUTF8="1",
        PYTHONPATH=str(guard) + os.pathsep + str(ROOT),
        NODE_OPTIONS='--require="' + (guard / "network.cjs").as_posix() + '"',
        npm_config_offline="true",
        npm_config_audit="false",
        npm_config_update_notifier="false",
        NO_COLOR="1",
        PATH=str(Path(sys.executable).parent) + os.pathsep + env["PATH"],
        AUGPHYS_OFFLINE_LOG=str(CACHE / "network-probes.jsonl"),
    )
    for name in ("network-probes.jsonl", "network-runtime.jsonl"):
        (CACHE / name).write_text("", encoding="utf-8")
    python_probe = (
        "import socket\ntry:\n socket.socket().connect(('192.0.2.1', 9))\n"
        "except PermissionError:\n print('external connection blocked')\n"
        "else:\n raise SystemExit('guard did not block')"
    )
    node_probe = (
        "try { require('node:net').connect({host:'192.0.2.1',port:9}); process.exit(2); }"
        "catch (e) { if (!e.message.includes('M0 verification')) throw e; "
        "console.log('external connection blocked'); }"
    )
    run([sys.executable, "-c", python_probe], "python-network-probe", env)
    run(["node", "-e", node_probe], "node-network-probe", env)
    env["AUGPHYS_OFFLINE_LOG"] = str(CACHE / "network-runtime.jsonl")
    summary = {
        "source_commit": commit,
        "network_scope": "external IP blocked; loopback/IPC allowed",
    }
    server = None
    server_output = None
    source.rename(hidden)
    try:
        assert not source.exists() and hidden.exists()
        summary["original_source_absent"] = True
        if not args.browser_only:
            run([sys.executable, "manage.py", "test"], "test", env)
            summary["test"] = "passed"
            run([sys.executable, "manage.py", "check"], "check", env)
            summary["check"] = "passed"
        else:
            summary["test"] = summary["check"] = "not rerun (focused browser verification)"
        # A single server process makes cleanup reliable even after a failed gate.
        # Owners may have supplied models since M0. Exercise degradation with
        # child-only overrides instead of moving or modifying their weights.
        absent = CACHE / "intentionally-absent-models"
        if absent.exists():
            raise RuntimeError("The missing-model verification path must not exist")
        server_env = {
            **env,
            "CIRCUIT_MODEL": str(absent / "circuit.pt"),
            "CIRCUIT_RAPIDOCR_DET": str(absent / "det.onnx"),
            "CIRCUIT_RAPIDOCR_REC": str(absent / "rec.onnx"),
            "CIRCUIT_RAPIDOCR_CLS": str(absent / "cls.onnx"),
            "CIRCUIT_EASYOCR_MODELS": str(absent / "easyocr"),
        }
        server_output = (CACHE / "server.log").open("w", encoding="utf-8")
        server = subprocess.Popen(
            [
                sys.executable,
                "-m",
                "uvicorn",
                "backend.app.main:app",
                "--host",
                "127.0.0.1",
                "--port",
                "8000",
            ],
            cwd=ROOT,
            env=server_env,
            stdout=server_output,
            stderr=subprocess.STDOUT,
            creationflags=subprocess.CREATE_NO_WINDOW if os.name == "nt" else 0,
        )
        deadline = time.monotonic() + 60
        while True:
            if server.poll() is not None:
                raise RuntimeError("Verification server exited; check server.log")
            try:
                health = http_json("/api/health")
                if health["detector"] == "missing_weights" and health["ocr"] != "warming":
                    break
            except OSError:
                pass
            if time.monotonic() >= deadline:
                raise RuntimeError(
                    "Verification server did not reach explicit missing-model health"
                )
            time.sleep(0.2)
        summary["health"] = health
        with urllib.request.urlopen("http://127.0.0.1:8000", timeout=10) as response:
            assert response.status == 200 and b'<div id="app"' in response.read()
        boundary = "m0-" + uuid.uuid4().hex
        raster = (ROOT / "frontend/public/demos/mixed-network.png").read_bytes()
        body = (
            (
                f'--{boundary}\r\nContent-Disposition: form-data; name="image"; filename="diagram.png"'
                "\r\nContent-Type: image/png\r\n\r\n"
            ).encode()
            + raster
            + f"\r\n--{boundary}--\r\n".encode()
        )
        result = http_json(
            "/api/analyze", body, {"Content-Type": "multipart/form-data; boundary=" + boundary}
        )
        assert result["provenance"] == "demo_fallback"
        assert any(w["code"] == "detector_unavailable" for w in result["warnings"])
        summary["missing_weights_analysis"] = {
            "provenance": result["provenance"],
            "detector_unavailable": True,
            "response_keys": sorted(result),
        }
        summary["served"] = "http://127.0.0.1:8000"
        if args.browser:
            if args.browser_filter:
                summary["browser_filter"] = args.browser_filter
                summary["browser_repeat"] = args.browser_repeat
                run(
                    [
                        "npx.cmd" if os.name == "nt" else "npx",
                        "playwright",
                        "test",
                        "--grep",
                        args.browser_filter,
                        "--repeat-each",
                        str(args.browser_repeat),
                    ],
                    "browser",
                    env,
                    timeout=900,
                    cwd=ROOT / "frontend",
                )
            else:
                run([sys.executable, "manage.py", "browser"], "browser", env, timeout=900)
            summary["browser"] = "passed"
        attempts = (CACHE / "network-runtime.jsonl").read_text(encoding="utf-8").splitlines()
        summary["blocked_runtime_external_attempts"] = len(attempts)
        if attempts:
            raise RuntimeError(
                "Runtime attempted external network access; inspect network-runtime.jsonl"
            )
    finally:
        if server is not None:
            server.terminate()
            try:
                server.wait(timeout=15)
            except subprocess.TimeoutExpired:
                server.kill()
                server.wait(timeout=10)
        if server_output is not None:
            server_output.close()
        if hidden.exists() and not source.exists():
            hidden.rename(source)
        summary["source_restored"] = source.exists() and not hidden.exists()
        summary["blocked_runtime_external_attempts"] = len(
            (CACHE / "network-runtime.jsonl").read_text(encoding="utf-8").splitlines()
        )
        (CACHE / "summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
        print(json.dumps(summary, indent=2), flush=True)


if __name__ == "__main__":
    main()
