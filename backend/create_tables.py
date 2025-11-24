from app.db.session import engine
from app.db.base import Base
from sqlalchemy import text   # 👈 ДОБАВИЛИ ЭТО


def main():
    print("Creating tables...")
    Base.metadata.create_all(bind=engine)
    print("Tables created.")

    # 🔧 Одноразовый фикс для таблицы payments
    ddl = "ALTER TABLE payments ADD COLUMN telegram_id BIGINT"
    print("Trying to add column telegram_id to payments...")
    with engine.connect() as conn:
        try:
            conn.execute(text(ddl))
            print("✅ Column telegram_id added to payments")
        except Exception as e:
            # Если колонка уже есть или другая ошибка — просто не падаем
            print("ℹ️ Skipping ALTER TABLE payments:", e)


if __name__ == "__main__":
    main()