from sqlalchemy import text
from app.db.session import engine
from app.db.base import Base


def show_columns(conn):
    rows = conn.execute(
        text(
            "SELECT column_name FROM information_schema.columns "
            "WHERE table_name = 'payments' ORDER BY column_name"
        )
    ).fetchall()
    print("Columns in payments:", [r[0] for r in rows])


def main():
    print("=== Using DB:", engine.url, "===")

    # сначала покажем, что было
    with engine.begin() as conn:
        print("=== BEFORE DROP ===")
        show_columns(conn)

        print("Dropping table payments (if exists)...")
        conn.execute(text("DROP TABLE IF EXISTS payments CASCADE"))
        print("✅ payments dropped")

    # создаём все таблицы по моделям
    print("Creating tables from models...")
    Base.metadata.create_all(bind=engine)
    print("Tables created.")

    # смотрим, что стало с payments
    with engine.begin() as conn:
        print("=== AFTER CREATE ===")
        show_columns(conn)


if __name__ == "__main__":
    main()
