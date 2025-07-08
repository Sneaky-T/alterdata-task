from app.db import Base
from sqlalchemy import Column, DateTime, ForeignKey, Numeric, String, Integer
from sqlalchemy.dialects.postgresql import UUID
from datetime import datetime, timezone
import uuid


class Transaction(Base):
    __tablename__ = "transactions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    customer_id = Column(UUID(as_uuid=True), nullable=False)
    product_id = Column(UUID(as_uuid=True), nullable=False)
    amount = Column(Numeric(10, 2), nullable=False)
    currency = Column(String(3), nullable=False)
    quantity = Column(Integer, nullable=False)
    timestamp = Column(DateTime, nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
