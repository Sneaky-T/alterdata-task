from typing import Annotated
from pydantic import BaseModel, condecimal, conint, ConfigDict
from uuid import UUID
from datetime import datetime
from enum import Enum


class CurrencyEnum(str, Enum):
    USD = "USD"
    EUR = "EUR"
    PLN = "PLN"


class Transaction(BaseModel):
    transaction_id: UUID
    customer_id: UUID
    product_id: UUID
    amount: Annotated[float, condecimal(max_digits=10, decimal_places=2)]
    currency: CurrencyEnum
    quantity: Annotated[int, conint(gt=0)]
    timestamp: datetime


class TransactionPost(Transaction):
    pass


class TransactionGet(Transaction):
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)
