"""One-off verification of W1·D4 migration (run from server/)."""

from sqlalchemy import text

from app.db.session import get_engine


def main() -> None:
    engine = get_engine()
    with engine.connect() as conn:
        tables = [
            row[0]
            for row in conn.execute(
                text("SELECT tablename FROM pg_tables WHERE schemaname = 'public' ORDER BY 1")
            )
        ]
        hypertables = [
            row[0]
            for row in conn.execute(
                text("SELECT hypertable_name FROM timescaledb_information.hypertables")
            )
        ]
        caggs = [
            row[0]
            for row in conn.execute(
                text("SELECT view_name FROM timescaledb_information.continuous_aggregates")
            )
        ]
        print("tables", tables)
        print("hypertables", hypertables)
        print("caggs", caggs)


if __name__ == "__main__":
    main()
