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

    # создаём таблицы, если их ещё нет
    Base.metadata.create_all(bind=engine)
    print("Tables created (if not existed).")

    # ВАЖНО: engine.begin() -> транзакция с автоматическим COMMIT
    with engine.begin() as conn:
        print("=== BEFORE ALTER ===")
        show_columns(conn)

        ddl = "ALTER TABLE payments ADD COLUMN telegram_id BIGINT"
        print("Trying to add column telegram_id to payments...")

        try:
            conn.execute(text(ddl))
            print("✅ Column telegram_id added")
        except Exception as e:
            print("ℹ️ ALTER TABLE error (maybe column exists):", e)

        print("=== AFTER ALTER ===")
        show_columns(conn)


if __name__ == "__main__":
    main()
