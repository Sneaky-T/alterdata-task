from fastapi import APIRouter, Depends, Query
from app.db import Session, get_db
from uuid import UUID
from app.schemas.customer_report import CustomerSummaryGet
from app.logic.customer_summary import return_customer_summary
from datetime import datetime
from typing import Optional

customer_summary_router = APIRouter(
    prefix="/customer-summary", tags=["customer-summary"]
)


@customer_summary_router.get("/{customer_id}", response_model=CustomerSummaryGet)
def get_customer_summary(
    customer_id: UUID,
    start_date: Optional[datetime] = Query(None),
    end_date: Optional[datetime] = Query(None),
    db: Session = Depends(get_db),
) -> CustomerSummaryGet:
    return return_customer_summary(customer_id, start_date, end_date, db)
