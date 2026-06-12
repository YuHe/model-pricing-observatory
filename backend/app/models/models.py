from __future__ import annotations

import uuid
from datetime import date, datetime
from decimal import Decimal
from typing import Optional, List

from sqlalchemy import String, Boolean, Integer, Date, DateTime, Text, Numeric, ForeignKey, UniqueConstraint, JSON
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from app.database import Base


class Provider(Base):
    __tablename__ = "provider"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    type: Mapped[str] = mapped_column(String(20), nullable=False)
    country: Mapped[Optional[str]] = mapped_column(String(10))
    official_url: Mapped[Optional[str]] = mapped_column(Text)
    logo_url: Mapped[Optional[str]] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    models: Mapped[List["Model"]] = relationship(back_populates="provider")


class Model(Base):
    __tablename__ = "model"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    provider_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("provider.id"), nullable=False)
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    family: Mapped[Optional[str]] = mapped_column(String(100))
    release_date: Mapped[Optional[date]] = mapped_column(Date)
    description: Mapped[Optional[str]] = mapped_column(Text)
    status: Mapped[str] = mapped_column(String(20), default="active")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    provider: Mapped["Provider"] = relationship(back_populates="models")
    capability: Mapped[Optional["ModelCapability"]] = relationship(back_populates="model", uselist=False)
    aliases: Mapped[List["ModelAlias"]] = relationship(back_populates="model")

    __table_args__ = (UniqueConstraint("provider_id", "name"),)


class ModelCapability(Base):
    __tablename__ = "model_capability"

    model_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("model.id"), primary_key=True)
    context_window: Mapped[Optional[int]] = mapped_column(Integer)
    max_output_tokens: Mapped[Optional[int]] = mapped_column(Integer)
    vision: Mapped[bool] = mapped_column(Boolean, default=False)
    reasoning: Mapped[bool] = mapped_column(Boolean, default=False)
    tool_calling: Mapped[bool] = mapped_column(Boolean, default=False)
    structured_output: Mapped[bool] = mapped_column(Boolean, default=False)
    json_mode: Mapped[bool] = mapped_column(Boolean, default=False)
    batch_api: Mapped[bool] = mapped_column(Boolean, default=False)
    fine_tuning: Mapped[bool] = mapped_column(Boolean, default=False)
    prompt_caching: Mapped[bool] = mapped_column(Boolean, default=False)

    model: Mapped["Model"] = relationship(back_populates="capability")


class ModelAlias(Base):
    __tablename__ = "model_alias"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    model_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("model.id"), nullable=False)
    alias_name: Mapped[str] = mapped_column(String(300), nullable=False)
    source: Mapped[str] = mapped_column(String(100), nullable=False)

    model: Mapped["Model"] = relationship(back_populates="aliases")

    __table_args__ = (UniqueConstraint("alias_name", "source"),)


class PriceSnapshot(Base):
    __tablename__ = "price_snapshot"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    date: Mapped[date] = mapped_column(Date, nullable=False)
    model_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("model.id"), nullable=False)
    channel_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("provider.id"), nullable=False)
    currency: Mapped[str] = mapped_column(String(10), nullable=False)
    input_price_per_m: Mapped[Optional[Decimal]] = mapped_column(Numeric(12, 6))
    output_price_per_m: Mapped[Optional[Decimal]] = mapped_column(Numeric(12, 6))
    input_price_cny: Mapped[Optional[Decimal]] = mapped_column(Numeric(12, 6))
    output_price_cny: Mapped[Optional[Decimal]] = mapped_column(Numeric(12, 6))
    exchange_rate: Mapped[Optional[Decimal]] = mapped_column(Numeric(10, 4))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    __table_args__ = (UniqueConstraint("date", "model_id", "channel_id"),)


class SubscriptionPlan(Base):
    __tablename__ = "subscription_plan"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    provider: Mapped[str] = mapped_column(String(100), nullable=False)
    plan_name: Mapped[str] = mapped_column(String(200), nullable=False)
    monthly_price: Mapped[Optional[Decimal]] = mapped_column(Numeric(10, 2))
    annual_price: Mapped[Optional[Decimal]] = mapped_column(Numeric(10, 2))
    currency: Mapped[str] = mapped_column(String(10), nullable=False)
    monthly_price_cny: Mapped[Optional[Decimal]] = mapped_column(Numeric(10, 2))
    features: Mapped[Optional[dict]] = mapped_column(JSON)
    source_url: Mapped[Optional[str]] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    __table_args__ = (UniqueConstraint("provider", "plan_name"),)


class SubscriptionSnapshot(Base):
    __tablename__ = "subscription_snapshot"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    date: Mapped[date] = mapped_column(Date, nullable=False)
    plan_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("subscription_plan.id"), nullable=False)
    monthly_price: Mapped[Optional[Decimal]] = mapped_column(Numeric(10, 2))
    monthly_price_cny: Mapped[Optional[Decimal]] = mapped_column(Numeric(10, 2))
    exchange_rate: Mapped[Optional[Decimal]] = mapped_column(Numeric(10, 4))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    __table_args__ = (UniqueConstraint("date", "plan_id"),)


class ExchangeRate(Base):
    __tablename__ = "exchange_rate"

    date: Mapped[date] = mapped_column(Date, primary_key=True)
    usd_cny: Mapped[Decimal] = mapped_column(Numeric(10, 4), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


class CrawlJob(Base):
    __tablename__ = "crawl_job"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    source: Mapped[str] = mapped_column(String(100), nullable=False)
    status: Mapped[str] = mapped_column(String(20), nullable=False)
    started_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    finished_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    models_synced: Mapped[int] = mapped_column(Integer, default=0)
    error_message: Mapped[Optional[str]] = mapped_column(Text)
    stack_trace: Mapped[Optional[str]] = mapped_column(Text)
    retry_count: Mapped[int] = mapped_column(Integer, default=0)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


class AlertConfig(Base):
    __tablename__ = "alert_config"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    type: Mapped[str] = mapped_column(String(20), nullable=False)
    endpoint: Mapped[str] = mapped_column(Text, nullable=False)
    enabled: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


class AlertLog(Base):
    __tablename__ = "alert_log"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    alert_config_id: Mapped[Optional[uuid.UUID]] = mapped_column(UUID(as_uuid=True), ForeignKey("alert_config.id"))
    job_id: Mapped[Optional[uuid.UUID]] = mapped_column(UUID(as_uuid=True), ForeignKey("crawl_job.id"))
    sent_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    status: Mapped[Optional[str]] = mapped_column(String(20))
    error_message: Mapped[Optional[str]] = mapped_column(Text)
