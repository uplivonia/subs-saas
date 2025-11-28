from datetime import datetime
from sqlalchemy import Column, Integer, BigInteger, String, DateTime, Boolean, Text
from app.db.base_class import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    telegram_id = Column(BigInteger, unique=True, index=True, nullable=False)
    name = Column(String, nullable=True)
    username = Column(String, nullable=True)
    language = Column(String, default="en")
    created_at = Column(DateTime, default=datetime.utcnow)

    # OLD: for Stripe Connect (можем не использовать, но пусть лежит на будущее)
    stripe_account_id = Column(String, nullable=True)
    stripe_onboarded = Column(Boolean, default=False)

    # NEW: внутренний кошелёк и реквизиты для выплат
    # баланс храним в центах, чтобы не ловить проблемы с float
    balance_cents = Column(BigInteger, nullable=False, server_default="0")

    # пример: "sepa", "revolut", "wise", "paypal", "crypto" и т.п.
    payout_method = Column(String, nullable=True)

    # сюда можно положить IBAN, номер карты, юзернейм Revolut и т.п.
    # пока просто TEXT, дальше можем сделать JSON
    payout_details = Column(Text, nullable=True)
