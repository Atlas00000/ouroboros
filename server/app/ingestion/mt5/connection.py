"""MT5 terminal connectivity."""

from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import Any

from app.config import Settings, get_settings

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class Mt5ConnectionInfo:
    connected: bool
    login: int | None
    server: str | None
    company: str | None
    terminal_build: int | None
    error: str | None = None


def _import_mt5() -> Any:
    try:
        import MetaTrader5 as mt5  # type: ignore[import-untyped]
    except ImportError as exc:  # pragma: no cover
        raise RuntimeError(
            "MetaTrader5 package is not installed. pip install MetaTrader5"
        ) from exc
    return mt5


def connect(settings: Settings | None = None) -> Mt5ConnectionInfo:
    """Initialize and log in to the local MT5 terminal."""
    cfg = settings or get_settings()
    mt5 = _import_mt5()

    if not cfg.mt5_path:
        return Mt5ConnectionInfo(
            connected=False,
            login=cfg.mt5_login,
            server=cfg.mt5_server,
            company=None,
            terminal_build=None,
            error="MT5_PATH is not set",
        )

    initialized = mt5.initialize(path=cfg.mt5_path)
    if not initialized:
        code, message = mt5.last_error()
        return Mt5ConnectionInfo(
            connected=False,
            login=cfg.mt5_login,
            server=cfg.mt5_server,
            company=None,
            terminal_build=None,
            error=f"initialize failed: {code} {message}",
        )

    if cfg.mt5_login and cfg.mt5_password and cfg.mt5_server:
        authorized = mt5.login(
            login=int(cfg.mt5_login),
            password=cfg.mt5_password,
            server=cfg.mt5_server,
        )
        if not authorized:
            code, message = mt5.last_error()
            mt5.shutdown()
            return Mt5ConnectionInfo(
                connected=False,
                login=cfg.mt5_login,
                server=cfg.mt5_server,
                company=None,
                terminal_build=None,
                error=f"login failed: {code} {message}",
            )

    account = mt5.account_info()
    terminal = mt5.terminal_info()
    info = Mt5ConnectionInfo(
        connected=True,
        login=int(account.login) if account else cfg.mt5_login,
        server=account.server if account else cfg.mt5_server,
        company=account.company if account else cfg.mt5_broker,
        terminal_build=int(terminal.build) if terminal else None,
    )
    logger.info(
        "mt5_connected login=%s server=%s build=%s",
        info.login,
        info.server,
        info.terminal_build,
    )
    return info


def disconnect() -> None:
    mt5 = _import_mt5()
    mt5.shutdown()
    logger.info("mt5_disconnected")


def ensure_connected(settings: Settings | None = None) -> Mt5ConnectionInfo:
    """Connect if needed; returns connection info (raises on hard failure)."""
    info = connect(settings)
    if not info.connected:
        raise RuntimeError(info.error or "MT5 connection failed")
    return info
