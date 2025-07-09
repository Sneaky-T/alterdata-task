from app.db import Session
from app.models.transaction import Transaction
from app.schemas.customer_report import CustomerSummaryGet
from app.schemas.product_report import ProductSummaryGet
from sqlalchemy import func, case
from uuid import UUID
from fastapi import HTTPException
from typing import Optional
from datetime import datetime
from sqlalchemy.exc import DataError, IntegrityError, OperationalError
import logging

logger = logging.getLogger(__name__)

currency_rate = case(
    (Transaction.currency == "USD", Transaction.amount * 4.0),
    (Transaction.currency == "EUR", Transaction.amount * 4.3),
    else_=Transaction.amount,
)


def return_customer_summary(
    customer_id: UUID,
    start_date: Optional[datetime],
    end_date: Optional[datetime],
    db: Session,
) -> CustomerSummaryGet:
    try:
        customer_summary = db.query(
            func.round(func.sum(currency_rate), 2).label("total_amount_in_PLN"),
            func.count(func.distinct(Transaction.product_id)).label(
                "unique_product_count"
            ),
            func.max(Transaction.timestamp).label("last_transaction_date"),
        ).filter(Transaction.customer_id == customer_id)

        if start_date:
            customer_summary = customer_summary.filter(
                Transaction.timestamp >= start_date
            )
        if end_date:
            customer_summary = customer_summary.filter(
                Transaction.timestamp <= end_date
            )

        result = customer_summary.first()
        if not result:
            logger.warning(f"Customer not found: {customer_id}")
            raise HTTPException(status_code=404, detail="Customer not found.")
        return CustomerSummaryGet.model_validate(result)
    except (DataError, IntegrityError, OperationalError) as e:
        logger.error(
            f"Database error in return_customer_summary: {type(e).__name__}: {e}"
        )
        raise HTTPException(
            status_code=500, detail=f"Database error: {type(e).__name__}: {e}"
        )
    except Exception as e:
        logger.exception("Unexpected error in return_customer_summary")
        raise HTTPException(
            status_code=500, detail=f"Unexpected error: {type(e).__name__}: {e}"
        )


def return_product_summary(
    product_id: UUID,
    start_date: Optional[datetime],
    end_date: Optional[datetime],
    db: Session,
) -> ProductSummaryGet:
    try:
        product_summary = db.query(
            func.sum(Transaction.quantity).label("total_quantity"),
            func.round(func.sum(currency_rate), 2).label("total_amount_in_PLN"),
            func.count(func.distinct(Transaction.customer_id)).label(
                "unique_customer_count"
            ),
        ).filter(Transaction.product_id == product_id)

        if start_date:
            product_summary = product_summary.filter(
                Transaction.timestamp >= start_date
            )
        if end_date:
            product_summary = product_summary.filter(Transaction.timestamp <= end_date)

        result = product_summary.first()
        if not result:
            logger.warning(f"Product not found: {product_id}")
            raise HTTPException(status_code=404, detail="Product not found.")
        return ProductSummaryGet.model_validate(result)
    except (DataError, IntegrityError, OperationalError) as e:
        logger.error(
            f"Database error in return_product_summary: {type(e).__name__}: {e}"
        )
        raise HTTPException(
            status_code=500, detail=f"Database error: {type(e).__name__}: {e}"
        )
    except Exception as e:
        logger.exception("Unexpected error in return_product_summary")
        raise HTTPException(
            status_code=500, detail=f"Unexpected error: {type(e).__name__}: {e}"
        )
