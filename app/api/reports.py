from fastapi import APIRouter, Depends, Query
from uuid import UUID
from app.db import Session, get_db
from datetime import datetime
from typing import Optional
from app.logic.reports import return_customer_summary, return_product_summary
from app.schemas.customer_report import CustomerSummaryGet
from app.schemas.product_report import ProductSummaryGet
import logging

logger = logging.getLogger(__name__)

reports_router = APIRouter(prefix="/reports", tags=["reports"])


@reports_router.get(
    "/customer-summary/{customer_id}", response_model=CustomerSummaryGet
)
def get_customer_summary(
    customer_id: UUID,
    start_date: Optional[datetime] = Query(None),
    end_date: Optional[datetime] = Query(None),
    db: Session = Depends(get_db),
) -> CustomerSummaryGet:
    logger.info(
        f"Customer summary requested: {customer_id}, start_date={start_date}, end_date={end_date}"
    )
    return return_customer_summary(customer_id, start_date, end_date, db)


@reports_router.get("/product-summary/{product_id}", response_model=ProductSummaryGet)
def get_product_summary(
    product_id: UUID,
    start_date: Optional[datetime] = Query(None),
    end_date: Optional[datetime] = Query(None),
    db: Session = Depends(get_db),
) -> ProductSummaryGet:
    logger.info(
        f"Product summary requested: {product_id}, start_date={start_date}, end_date={end_date}"
    )
    return return_product_summary(product_id, start_date, end_date, db)
