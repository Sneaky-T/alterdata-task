from pydantic import BaseModel, ConfigDict, condecimal, conint
from typing import Annotated
from datetime import datetime


class CustomerSummaryGet(BaseModel):
    total_amount_in_PLN: Annotated[float, condecimal(max_digits=13, decimal_places=2)]
    unique_product_count: Annotated[int, conint(ge=1)]
    last_transaction_date: datetime
    model_config = ConfigDict(from_attributes=True)
