"""Shared helpers for Postgres dump/restore via docker exec."""

from __future__ import annotations

import os
import subprocess
import sys
from datetime import UTC, datetime
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_CONTAINER = os.environ.get("OUROBOROS_PG_CONTAINER", "ouroboros-postgres")
DEFAULT_USER = os.environ.get("POSTGRES_USER", "ouroboros")
DEFAULT_DB = os.environ.get("POSTGRES_DB", "ouroboros")
BACKUP_ROOT = Path(os.environ.get("OUROBOROS_BACKUP_DIR", REPO_ROOT / "data" / "backups"))

# Irreplaceable tables (N9): not cheaply re-backfillable from MT5.
IRREPLACEABLE_TABLES = (
    "sentiment",
    "forecast_log",
    "outbox",
    "profiles",
    "insights",
    "news",
    "states",
    "source_registry",
    "assets",
)


def stamp() -> str:
    return datetime.now(UTC).strftime("%Y%m%dT%H%M%SZ")


def ensure_backup_dir(kind: str) -> Path:
    path = BACKUP_ROOT / kind
    path.mkdir(parents=True, exist_ok=True)
    return path


def run(cmd: list[str], *, check: bool = True) -> subprocess.CompletedProcess[str]:
    print("+", " ".join(cmd), flush=True)
    return subprocess.run(cmd, check=check, text=True, capture_output=True)


def docker_available(container: str = DEFAULT_CONTAINER) -> bool:
    try:
        r = run(["docker", "inspect", "-f", "{{.State.Running}}", container], check=False)
        return r.returncode == 0 and r.stdout.strip() == "true"
    except FileNotFoundError:
        return False


def pg_dump_custom(
    *,
    outfile: Path,
    db: str = DEFAULT_DB,
    user: str = DEFAULT_USER,
    container: str = DEFAULT_CONTAINER,
    tables: tuple[str, ...] | None = None,
) -> Path:
    """
    Dump to custom format (-Fc) inside the container, then docker cp out.

    Custom format is required for selective pg_restore.
    """
    if not docker_available(container):
        raise RuntimeError(
            f"Postgres container {container!r} is not running. "
            "Start with: docker compose up -d postgres"
        )

    remote = f"/tmp/ouroboros_dump_{stamp()}.dump"
    cmd = [
        "docker",
        "exec",
        container,
        "pg_dump",
        "-U",
        user,
        "-d",
        db,
        "-Fc",
        "--no-owner",
        "--no-acl",
        "-f",
        remote,
    ]
    if tables:
        for t in tables:
            cmd.extend(["-t", t])

    result = run(cmd, check=False)
    if result.returncode != 0:
        sys.stderr.write(result.stderr)
        raise RuntimeError(f"pg_dump failed: {result.stderr.strip()}")

    outfile.parent.mkdir(parents=True, exist_ok=True)
    cp = run(["docker", "cp", f"{container}:{remote}", str(outfile)], check=False)
    run(["docker", "exec", container, "rm", "-f", remote], check=False)
    if cp.returncode != 0:
        raise RuntimeError(f"docker cp failed: {cp.stderr.strip()}")
    return outfile


def ensure_database(
    name: str,
    *,
    user: str = DEFAULT_USER,
    container: str = DEFAULT_CONTAINER,
) -> None:
    exists = run(
        [
            "docker",
            "exec",
            "-e",
            f"PGPASSWORD={os.environ.get('POSTGRES_PASSWORD', 'ouroboros')}",
            container,
            "psql",
            "-U",
            user,
            "-d",
            "postgres",
            "-tAc",
            f"SELECT 1 FROM pg_database WHERE datname = '{name}'",
        ],
        check=False,
    )
    if exists.stdout.strip() == "1":
        return
    run(
        [
            "docker",
            "exec",
            container,
            "psql",
            "-U",
            user,
            "-d",
            "postgres",
            "-c",
            f"CREATE DATABASE {name}",
        ]
    )


def drop_database(
    name: str,
    *,
    user: str = DEFAULT_USER,
    container: str = DEFAULT_CONTAINER,
) -> None:
    run(
        [
            "docker",
            "exec",
            container,
            "psql",
            "-U",
            user,
            "-d",
            "postgres",
            "-c",
            (
                f"SELECT pg_terminate_backend(pid) FROM pg_stat_activity "
                f"WHERE datname = '{name}' AND pid <> pg_backend_pid();"
            ),
        ],
        check=False,
    )
    run(
        [
            "docker",
            "exec",
            container,
            "psql",
            "-U",
            user,
            "-d",
            "postgres",
            "-c",
            f"DROP DATABASE IF EXISTS {name}",
        ]
    )


def pg_restore_custom(
    *,
    dump_path: Path,
    db: str,
    user: str = DEFAULT_USER,
    container: str = DEFAULT_CONTAINER,
    clean: bool = False,
) -> None:
    remote = f"/tmp/ouroboros_restore_{stamp()}.dump"
    run(["docker", "cp", str(dump_path), f"{container}:{remote}"])
    cmd = [
        "docker",
        "exec",
        container,
        "pg_restore",
        "-U",
        user,
        "-d",
        db,
        "--no-owner",
        "--no-acl",
    ]
    if clean:
        cmd.append("--clean")
        cmd.append("--if-exists")
    cmd.append(remote)
    result = run(cmd, check=False)
    run(["docker", "exec", container, "rm", "-f", remote], check=False)
    # pg_restore returns 1 on some non-fatal warnings (e.g. extension already exists)
    if result.returncode not in (0, 1):
        sys.stderr.write(result.stderr)
        raise RuntimeError(f"pg_restore failed ({result.returncode}): {result.stderr.strip()}")
    if result.stderr:
        sys.stderr.write(result.stderr)
