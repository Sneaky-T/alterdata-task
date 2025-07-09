from app.db import Session
from app.models.transaction import Transaction
from app.schemas.customer_report import CustomerSummaryGet
from sqlalchemy import func, case
from uuid import UUID
from fastapi import HTTPException
from typing import Optional
from datetime import datetime


def return_customer_summary(
    customer_id: UUID,
    start_date: Optional[datetime],
    end_date: Optional[datetime],
    db: Session,
) -> CustomerSummaryGet:
    currency_rate = case(
        (Transaction.currency == "USD", Transaction.amount * 4.0),
        (Transaction.currency == "EUR", Transaction.amount * 4.3),
        else_=Transaction.amount,
    )

    customer_summary = db.query(
        func.round(func.sum(currency_rate), 2).label("total_amount_in_PLN"),
        func.count(func.distinct(Transaction.product_id)).label("unique_product_count"),
        func.max(Transaction.timestamp).label("last_transaction_date"),
    ).filter(Transaction.customer_id == customer_id)

    if start_date:
        customer_summary = customer_summary.filter(Transaction.timestamp >= start_date)
    if end_date:
        customer_summary = customer_summary.filter(Transaction.timestamp <= end_date)

    if customer_summary := customer_summary.first():
        return CustomerSummaryGet.model_validate(customer_summary)
    else:
        raise HTTPException(status_code=404, detail="Customer not found.")
