"""Cross-platform runner. All generated state stays in this directory."""

import argparse
import os
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parent


def run(args, cwd=ROOT):
    return subprocess.run(args, cwd=cwd, check=True)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "command",
        choices=[
            "dev",
            "serve",
            "test",
            "check",
            "eval",
            "smoke",
            "browser",
            "build",
            "ocr-debug",
            "doctor",
        ],
    )
    parser.add_argument("image", nargs="?")
    parser.add_argument("--out", default=".cache/ocr-debug")
    args = parser.parse_args()
    npm = "npm.cmd" if os.name == "nt" else "npm"
    npx = "npx.cmd" if os.name == "nt" else "npx"
    env = dict(os.environ)
    env["PYTHONPATH"] = str(ROOT) + os.pathsep + env.get("PYTHONPATH", "")
    os.environ.update(env)
    if args.command == "doctor":
        run([sys.executable, "-m", "backend.tools.check_models"])
    elif args.command in {"test", "check"}:
        if args.command == "check":
            run(
                [
                    sys.executable,
                    "-m",
                    "ruff",
                    "check",
                    "backend",
                    "manage.py",
                    "bootstrap.py",
                    "tools",
                ]
            )
            run(
                [
                    sys.executable,
                    "-m",
                    "ruff",
                    "format",
                    "--check",
                    "backend",
                    "tools",
                    "manage.py",
                    "bootstrap.py",
                ]
            )
            run(
                [
                    npx,
                    "prettier",
                    "--check",
                    "src",
                    "tests",
                    "browser-tests",
                    "playwright.config.ts",
                    "vite.config.ts",
                    "tsconfig.json",
                    "package.json",
                ],
                ROOT / "frontend",
            )
        run([sys.executable, "-m", "pytest", "backend/tests", "-q"])
        run([npm, "test"], ROOT / "frontend")
        run([npm, "run", "build"], ROOT / "frontend")
    elif args.command == "ocr-debug":
        if not args.image:
            parser.error("ocr-debug requires an image path")
        run(
            [
                sys.executable,
                "-m",
                "backend.tools.ocr_debug",
                args.image,
                "--out",
                args.out,
            ]
        )
    elif args.command == "eval":
        run([sys.executable, "-m", "backend.tools.eval_e2e"])
    elif args.command == "smoke":
        run([sys.executable, "-m", "backend.tools.smoke"])
    elif args.command == "build":
        run([npm, "run", "build"], ROOT / "frontend")
    elif args.command == "browser":
        run([npx, "playwright", "test"], ROOT / "frontend")
    elif args.command == "serve":
        run(
            [
                sys.executable,
                "-m",
                "uvicorn",
                "backend.app.main:app",
                "--host",
                "127.0.0.1",
                "--port",
                "8000",
            ]
        )
    else:
        flags = subprocess.CREATE_NO_WINDOW if os.name == "nt" else 0
        api = subprocess.Popen(
            [
                sys.executable,
                "-m",
                "uvicorn",
                "backend.app.main:app",
                "--reload",
                "--reload-dir",
                str(ROOT / "backend"),
                "--host",
                "127.0.0.1",
                "--port",
                "8000",
            ],
            cwd=ROOT,
            env=env,
            creationflags=flags,
        )
        try:
            run([npm, "run", "dev"], ROOT / "frontend")
        finally:
            api.terminate()
            api.wait(timeout=10)


if __name__ == "__main__":
    main()
