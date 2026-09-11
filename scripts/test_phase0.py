#!/usr/bin/env python3
"""Phase 0 verification suite — run from repo root.

Usage:
  python scripts/test_phase0.py
  python scripts/test_phase0.py --quick          # skip Docker image builds
  python scripts/test_phase0.py --skip-compose   # assume services already up
"""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
import time
from collections.abc import Callable
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SERVER = ROOT / "server"
CONTRACTS = ROOT / "packages" / "contracts"
IS_WIN = os.name == "nt"


class StepError(RuntimeError):
    pass


def run(
    args: list[str],
    *,
    cwd: Path | None = None,
    env: dict[str, str] | None = None,
    check: bool = True,
) -> subprocess.CompletedProcess[str]:
    print(f"\n>> {' '.join(args)}" + (f"  (cwd={cwd})" if cwd else ""))
    merged = os.environ.copy()
    if env:
        merged.update(env)
    result = subprocess.run(
        args,
        cwd=str(cwd or ROOT),
        env=merged,
        text=True,
        capture_output=True,
    )
    if result.stdout:
        print(result.stdout.rstrip())
    if result.stderr:
        # keep noise but visible
        err = result.stderr.rstrip()
        if err:
            print(err)
    if check and result.returncode != 0:
        raise StepError(f"Command failed ({result.returncode}): {' '.join(args)}")
    return result


def compose_cmd() -> list[str]:
    # Prefer docker-compose (available on this machine); fall back to plugin.
    try:
        subprocess.run(
            ["docker-compose", "version"],
            capture_output=True,
            check=True,
        )
        return ["docker-compose"]
    except (FileNotFoundError, subprocess.CalledProcessError):
        return ["docker", "compose"]


def ensure_compose_up(skip: bool) -> None:
    if skip:
        print("\n== skip compose up ==")
        return
    cmd = compose_cmd()
    run([*cmd, "up", "-d"], cwd=ROOT)
    # wait for healthy
    for _ in range(30):
        ps = run([*cmd, "ps", "--format", "json"], cwd=ROOT, check=False)
        lines = [ln for ln in ps.stdout.splitlines() if ln.strip()]
        healthy = 0
        for ln in lines:
            try:
                row = json.loads(ln)
            except json.JSONDecodeError:
                continue
            if row.get("Health") == "healthy" or row.get("State") == "running":
                if row.get("Service") in {"postgres", "redis"}:
                    healthy += 1
        # docker-compose ps json may emit one object per line
        if healthy >= 2:
            print("Compose services look up.")
            return
        time.sleep(2)
    raise StepError("Postgres/Redis did not become healthy in time")


def pip_install() -> None:
    py = sys.executable
    run([py, "-m", "pip", "install", "-e", f"{CONTRACTS}[dev]", "-q"])
    run([py, "-m", "pip", "install", "-e", f"{SERVER}[dev]", "-q"], cwd=SERVER)


def migrate() -> None:
    env = {
        "DATABASE_URL": os.environ.get(
            "DATABASE_URL",
            "postgresql://ouroboros:ouroboros@localhost:5433/ouroboros",
        ),
        "REDIS_URL": os.environ.get("REDIS_URL", "redis://localhost:6380/0"),
    }
    run([sys.executable, "-m", "alembic", "upgrade", "head"], cwd=SERVER, env=env)


def ruff() -> None:
    run([sys.executable, "-m", "ruff", "check", "app", "tests"], cwd=SERVER)


def alembic_check() -> None:
    env = {
        "DATABASE_URL": os.environ.get(
            "DATABASE_URL",
            "postgresql://ouroboros:ouroboros@localhost:5433/ouroboros",
        ),
    }
    run([sys.executable, "-m", "alembic", "check"], cwd=SERVER, env=env)


def pytest_contracts() -> None:
    run(
        [sys.executable, "-m", "pytest", "-q", "tests"],
        cwd=CONTRACTS,
        env={"PYTHONPATH": str(CONTRACTS)},
    )


def pytest_server() -> None:
    env = {
        "DATABASE_URL": os.environ.get(
            "DATABASE_URL",
            "postgresql://ouroboros:ouroboros@localhost:5433/ouroboros",
        ),
        "REDIS_URL": os.environ.get("REDIS_URL", "redis://localhost:6380/0"),
        "APP_ENV": "test",
    }
    run([sys.executable, "-m", "pytest", "-q"], cwd=SERVER, env=env)


def export_jsonschema() -> None:
    run([sys.executable, "-m", "contracts.export_jsonschema"], cwd=CONTRACTS)


def docker_builds() -> None:
    run(["docker", "build", "-t", "ouroboros-server:phase0", str(SERVER)])
    run(["docker", "build", "-t", "ouroboros-client:phase0", str(ROOT / "client")])


def structure_check() -> None:
    required = [
        ROOT / "client",
        ROOT / "server" / "app" / "main.py",
        ROOT / "packages" / "contracts" / "contracts" / "profile_v1.py",
        ROOT / "docker-compose.yml",
        ROOT / ".github" / "workflows" / "ci.yml",
        ROOT / "server" / "railway.toml",
        ROOT / "server" / "Dockerfile",
        ROOT / "client" / "Dockerfile",
    ]
    missing = [str(p.relative_to(ROOT)) for p in required if not p.exists()]
    if missing:
        raise StepError(f"Missing Phase 0 paths: {missing}")
    print("Structure check OK")


def main() -> int:
    parser = argparse.ArgumentParser(description="Run Phase 0 verification suite")
    parser.add_argument("--quick", action="store_true", help="Skip Docker image builds")
    parser.add_argument(
        "--skip-compose",
        action="store_true",
        help="Do not run docker-compose up",
    )
    args = parser.parse_args()

    steps: list[tuple[str, Callable[[], None]]] = [
        ("structure", structure_check),
        ("compose", lambda: ensure_compose_up(args.skip_compose)),
        ("install", pip_install),
        ("migrate", migrate),
        ("ruff", ruff),
        ("alembic_check", alembic_check),
        ("jsonschema_export", export_jsonschema),
        ("pytest_contracts", pytest_contracts),
        ("pytest_server", pytest_server),
    ]
    if not args.quick:
        steps.append(("docker_builds", docker_builds))

    results: list[tuple[str, str]] = []
    for name, fn in steps:
        print(f"\n{'=' * 60}\n== {name}\n{'=' * 60}")
        try:
            fn()
            results.append((name, "PASS"))
        except StepError as exc:
            print(f"FAIL: {exc}")
            results.append((name, "FAIL"))
            _print_summary(results)
            return 1
        except Exception as exc:  # noqa: BLE001
            print(f"FAIL: {exc}")
            results.append((name, "FAIL"))
            _print_summary(results)
            return 1

    _print_summary(results)
    print("\nPhase 0 verification: ALL PASSED")
    return 0


def _print_summary(results: list[tuple[str, str]]) -> None:
    print("\n---------- Phase 0 summary ----------")
    for name, status in results:
        print(f"  {status:4}  {name}")
    print("-------------------------------------")


if __name__ == "__main__":
    # Ensure server package imports resolve when cwd varies
    sys.path.insert(0, str(SERVER))
    sys.path.insert(0, str(CONTRACTS))
    raise SystemExit(main())
