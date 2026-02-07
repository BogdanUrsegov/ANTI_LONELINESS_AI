from sqlalchemy import Integer, DateTime, BigInteger, String
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy.sql import func
from datetime import datetime


class Base(DeclarativeBase):
    pass

class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    telegram_id: Mapped[int] = mapped_column(BigInteger, unique=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False
    )
    name: Mapped[str | None] = mapped_column(String(100), nullable=True)
    archetype: Mapped[str | None] = mapped_column(String(50), nullable=True)
    hard_time: Mapped[str | None] = mapped_column(String(50), nullable=True)  # или String, если коротко
    main_topic: Mapped[str | None] = mapped_column(String(50), nullable=True)