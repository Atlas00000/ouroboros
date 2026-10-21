"""Score EPG EURUSD magic 26101822 (P1 hard-stops) from latest Tester log."""
from __future__ import annotations

import runpy
from pathlib import Path

# Reuse P0 scorer with MAGIC override via exec of a thin wrapper.
src = Path(__file__).with_name("_score_magic_26101821.py").read_text(encoding="utf-8")
src = src.replace('MAGIC = "26101821"', 'MAGIC = "26101822"')
src = src.replace(
    'tester_magic_26101821_score.json',
    'tester_magic_26101822_score.json',
)
ns: dict = {"__name__": "__main__", "__file__": str(Path(__file__).resolve())}
exec(compile(src, str(Path(__file__).resolve()), "exec"), ns)
