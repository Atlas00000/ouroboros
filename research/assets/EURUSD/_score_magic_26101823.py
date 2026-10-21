"""Score EPG EURUSD magic 26101823 (P2 light selective) from latest Tester log."""
from pathlib import Path

src = Path(__file__).with_name("_score_magic_26101821.py").read_text(encoding="utf-8")
src = src.replace('MAGIC = "26101821"', 'MAGIC = "26101823"')
src = src.replace(
    "tester_magic_26101821_score.json",
    "tester_magic_26101823_score.json",
)
exec(compile(src, str(Path(__file__).resolve()), "exec"), {"__name__": "__main__", "__file__": str(Path(__file__).resolve())})
