"""Acceptance checks: thin symbols reach FX-like dossier planes."""

from __future__ import annotations

from dataclasses import dataclass

from sqlalchemy import text

from app.db.session import get_engine

THIN = [
    # Equities — news hard requirement
    ("AAPL", "equity", True),
    ("MSFT", "equity", True),
    ("NVDA", "equity", True),
    ("AMZN", "equity", True),
    ("META", "equity", True),
    ("GOOGL", "equity", True),
    ("TSLA", "equity", True),
    ("JPM", "equity", True),
    ("AVGO", "equity", True),
    ("XOM", "equity", True),
    # Energy / regional — news best-effort (group must be non-zero overall)
    ("XTIUSD", "energy", False),
    ("XBRUSD", "energy", False),
    ("DE40", "index", False),
    ("UK100", "index", False),
    ("JP225", "index", False),
]


@dataclass
class Row:
    symbol: str
    klass: str
    state_h1: int
    news: int
    sentiment: int
    insights: int
    require_news: bool

    @property
    def state_ok(self) -> bool:
        return self.state_h1 > 0

    @property
    def news_ok(self) -> bool:
        if self.require_news:
            return self.news > 0
        return True  # best-effort at row level

    @property
    def sentiment_ok(self) -> bool:
        # Required when news exists (scored path); else OK if no news
        if self.news <= 0:
            return True
        return self.sentiment > 0


def main() -> int:
    eng = get_engine()
    rows: list[Row] = []
    with eng.connect() as c:
        for sym, klass, req_news in THIN:
            state_h1 = int(
                c.execute(
                    text(
                        "SELECT count(*) FROM states WHERE symbol=:s AND timeframe='H1'"
                    ),
                    {"s": sym},
                ).scalar()
                or 0
            )
            news = int(
                c.execute(text("SELECT count(*) FROM news WHERE symbol=:s"), {"s": sym}).scalar()
                or 0
            )
            sent = int(
                c.execute(
                    text("SELECT count(*) FROM sentiment WHERE symbol=:s"), {"s": sym}
                ).scalar()
                or 0
            )
            insights = int(
                c.execute(
                    text("SELECT count(*) FROM insights WHERE symbol=:s"), {"s": sym}
                ).scalar()
                or 0
            )
            rows.append(
                Row(sym, klass, state_h1, news, sent, insights, req_news)
            )

    print("=" * 72)
    print("DOSSIER PARITY REPORT (equities / energy / regional indices)")
    print("=" * 72)
    print(f"{'SYM':8} {'CLASS':7} {'STATE':5} {'NEWS':5} {'SENT':5} {'INSI':5} RESULT")
    fails = 0
    for r in rows:
        ok = r.state_ok and r.news_ok and r.sentiment_ok
        if not ok:
            fails += 1
        mark = "OK" if ok else "XX"
        print(
            f"{r.symbol:8} {r.klass:7} {r.state_h1:5} {r.news:5} {r.sentiment:5} "
            f"{r.insights:5} [{mark}]"
        )

    soft = [r for r in rows if not r.require_news]
    soft_news = sum(r.news for r in soft)
    soft_ok = soft_news > 0
    print("-" * 72)
    print(
        f"energy/index news best-effort total={soft_news} "
        f"[{'OK' if soft_ok else 'XX'}]"
    )
    if not soft_ok:
        fails += 1

    equity_all_news = all(r.news > 0 for r in rows if r.require_news)
    print(f"equities all have news [{ 'OK' if equity_all_news else 'XX' }]")
    if not equity_all_news:
        fails += 1

    print("=" * 72)
    print(f"TOTAL fails={fails}")
    print("=" * 72)
    return 1 if fails else 0


if __name__ == "__main__":
    raise SystemExit(main())
