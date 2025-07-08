from typing import Annotated
from pydantic import BaseModel, condecimal, conint
from uuid import UUID
from datetime import datetime


class Transaction(BaseModel):
    customer_id: UUID
    product_id: UUID
    amount: Annotated[float, condecimal(max_digits=10, decimal_places=2)]
    currency: str
    quantity: Annotated[int, conint(gt=0)]
    timestamp: datetime


class TransactionPost(Transaction):
    pass


class TransactionGet(Transaction):
    id: UUID
    created_at: datetime

    class Config:
        from_attributes = True
