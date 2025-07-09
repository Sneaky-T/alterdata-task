from pydantic import BaseModel, ConfigDict, condecimal, conint
from typing import Annotated


class ProductSummaryGet(BaseModel):
    total_quantity: Annotated[int, conint(ge=1)]
    total_amount_in_PLN: Annotated[float, condecimal(max_digits=13, decimal_places=2)]
    unique_customer_count: Annotated[int, conint(ge=1)]
    model_config = ConfigDict(from_attributes=True)
