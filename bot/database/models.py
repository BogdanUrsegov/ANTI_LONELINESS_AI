from typing import Optional
from sqlalchemy import JSON, ForeignKey, Integer, DateTime, BigInteger, String, Boolean, Text, Index
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy.sql import func
from datetime import datetime


class Base(DeclarativeBase):
    """Базовый класс для всех моделей SQLAlchemy."""
    pass


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    telegram_id: Mapped[int] = mapped_column(BigInteger, unique=True, nullable=False, index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    
    name: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    archetype: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    hard_time: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    main_topic: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    # Настройки уведомлений
    notify_morning: Mapped[Optional[bool]] = mapped_column(Boolean, default=False)
    notify_morning_time: Mapped[Optional[str]] = mapped_column(String(5), nullable=True)  # HH:MM
    notify_evening: Mapped[Optional[bool]] = mapped_column(Boolean, default=False)
    notify_day_touches: Mapped[Optional[bool]] = mapped_column(Boolean, default=False)
    
    is_complete: Mapped[Optional[bool]] = mapped_column(Boolean, default=False)


class ChatMessage(Base):
    __tablename__ = "chat_messages"
    __table_args__ = (
        Index("ix_chat_messages_telegram_id_created", "telegram_id", "created_at"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    telegram_id: Mapped[int] = mapped_column(
        ForeignKey("users.telegram_id", ondelete="CASCADE"),
        nullable=False
    )
    role: Mapped[str] = mapped_column(String(20), nullable=False)  # user / assistant
    content: Mapped[str] = mapped_column(Text, nullable=False)
    reasoning_details: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)