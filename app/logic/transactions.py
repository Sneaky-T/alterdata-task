import logging
import csv
from app.db import SessionLocal
from app.models.transaction import Transaction
from app.schemas.transaction import TransactionPost
from pydantic import ValidationError
from sqlalchemy.exc import DataError, IntegrityError, OperationalError
import os
from typing import Optional
from uuid import UUID
from app.db import Session
from app.schemas.transaction import TransactionGet
from fastapi import HTTPException

logger = logging.getLogger(__name__)


def process_transactions(csv_file_tmp_path: str) -> None:
    try:
        with open(csv_file_tmp_path, "r", encoding="utf-8") as csv_file:
            transactions_csv = csv.DictReader(csv_file)

            rows_processed = 0
            rows_failed = 0

            for row in transactions_csv:
                rows_processed += 1
                try:
                    validated_row = TransactionPost(**row)  # type: ignore
                    with SessionLocal() as session:
                        with session.begin():
                            session.add(Transaction(**validated_row.model_dump()))
                except (
                    ValidationError,
                    KeyError,
                    ValueError,
                    DataError,
                    IntegrityError,
                    OperationalError,
                ) as e:
                    rows_failed += 1
                    logger.error(
                        f"Row {rows_processed}: {type(e).__name__}: {e} | {row}"
                    )
                except Exception as e:
                    logger.exception(f"Unexpected error in process_transactions: {e}")
                    raise HTTPException(
                        status_code=500,
                        detail=f"Unexpected error: {type(e).__name__}: {e}",
                    )

            message = f"Processed {rows_processed} rows, {rows_failed} rows failed."
            logger.info(message)
    finally:
        try:
            os.remove(csv_file_tmp_path)
        except OSError as cleanup_err:
            logger.error(
                f"Failed to remove temp file {csv_file_tmp_path}: {cleanup_err}"
            )
        except Exception as cleanup_err:
            logger.error(
                f"Unexpected error during temp file cleanup: {type(cleanup_err).__name__}: {cleanup_err}"
            )


def list_transactions(
    limit: int,
    offset: int,
    customer_id: Optional[UUID],
    product_id: Optional[UUID],
    db: Session,
) -> list[TransactionGet]:
    try:
        query = db.query(Transaction)
        if customer_id:
            query = query.filter(Transaction.customer_id == customer_id)
        if product_id:
            query = query.filter(Transaction.product_id == product_id)
        transactions_list = (
            query.order_by(Transaction.timestamp.desc())
            .offset(offset)
            .limit(limit)
            .all()
        )
        return [
            TransactionGet.model_validate(transaction)
            for transaction in transactions_list
        ]
    except (DataError, IntegrityError, OperationalError) as e:
        logger.error(f"Database error in list_transactions: {type(e).__name__}: {e}")
        raise HTTPException(
            status_code=500, detail=f"Database error: {type(e).__name__}: {e}"
        )
    except Exception as e:
        logger.exception("Unexpected error in list_transactions")
        raise HTTPException(
            status_code=500, detail=f"Unexpected error: {type(e).__name__}: {e}"
        )


def return_transaction(transaction_id: UUID, db: Session) -> TransactionGet:
    try:
        transaction = (
            db.query(Transaction)
            .filter(Transaction.transaction_id == transaction_id)
            .first()
        )
        if not transaction:
            logger.warning(f"Transaction not found: {transaction_id}")
            raise HTTPException(status_code=404, detail="Transaction not found")
        return TransactionGet.model_validate(transaction)
    except HTTPException:
        raise
    except (DataError, IntegrityError, OperationalError) as e:
        logger.error(f"Database error in return_transaction: {type(e).__name__}: {e}")
        raise HTTPException(
            status_code=500, detail=f"Database error: {type(e).__name__}: {e}"
        )
    except Exception as e:
        logger.exception("Unexpected error in return_transaction")
        raise HTTPException(
            status_code=500, detail=f"Unexpected error: {type(e).__name__}: {e}"
        )
