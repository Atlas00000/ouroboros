"""Smoke-test MT5 initialize + login using server/.env."""

from __future__ import annotations

import os
import sys
from pathlib import Path

SERVER_ROOT = Path(__file__).resolve().parents[2] / "server"
sys.path.insert(0, str(SERVER_ROOT))
os.chdir(SERVER_ROOT)

from app.config import get_settings  # noqa: E402
from app.ingestion.mt5.connection import connect, disconnect  # noqa: E402


def main() -> int:
    get_settings.cache_clear()
    settings = get_settings()
    print(f"path={settings.mt5_path}")
    print(
        f"login={settings.mt5_login} server={settings.mt5_server!r} "
        f"broker={settings.mt5_broker!r}"
    )

    # Probe initialize-only first (IPC)
    try:
        import MetaTrader5 as mt5
    except ImportError:
        print("FAILED: MetaTrader5 package missing")
        return 1

    if not mt5.initialize(path=settings.mt5_path):
        code, message = mt5.last_error()
        print(f"FAILED initialize (IPC): {code} {message}")
        print("Open MetaTrader 5 on this machine, enable Algo Trading, then retry.")
        return 1

    term = mt5.terminal_info()
    print(f"initialize OK build={getattr(term, 'build', None)} connected={getattr(term, 'connected', None)}")
    mt5.shutdown()

    info = connect(settings)
    if not info.connected:
        print(f"FAILED login: {info.error}")
        print(
            "Copy the exact Trade Server name from the MT5 login dialog "
            "(File → Login to Trade Account) into MT5_SERVER in server/.env."
        )
        return 1

    print(
        f"OK connected login={info.login} server={info.server!r} "
        f"company={info.company!r} build={info.terminal_build}"
    )
    disconnect()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
