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

csv_handler = logging.FileHandler("logs/csv_import.log")
csv_handler.setFormatter(logging.Formatter("%(asctime)s [%(levelname)s] %(message)s"))
csv_logger = logging.getLogger("csv_logger")
csv_logger.propagate = False
csv_logger.addHandler(csv_handler)
csv_logger.setLevel(logging.INFO)


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
                    Exception,
                ) as e:
                    rows_failed += 1
                    csv_logger.error(
                        f"Row {rows_processed}: {type(e).__name__}: {e} | {row}"
                    )

            message = f"Processed {rows_processed} rows, {rows_failed} rows failed."
            csv_logger.info(message)
            logging.info(message)
    finally:
        try:
            os.remove(csv_file_tmp_path)
        except Exception as cleanup_err:
            csv_logger.error(
                f"Failed to remove temp file {csv_file_tmp_path}: {cleanup_err}"
            )


def list_transactions(
    limit: int,
    offset: int,
    customer_id: Optional[UUID],
    product_id: Optional[UUID],
    db: Session,
) -> list[TransactionGet]:
    query = db.query(Transaction)
    if customer_id:
        query = query.filter(Transaction.customer_id == customer_id)
    if product_id:
        query = query.filter(Transaction.product_id == product_id)
    transactions_list = (
        query.order_by(Transaction.timestamp.desc()).offset(offset).limit(limit).all()
    )
    return [
        TransactionGet.model_validate(transaction) for transaction in transactions_list
    ]


def return_transaction(transaction_id: UUID, db: Session) -> TransactionGet:
    transaction = (
        db.query(Transaction)
        .filter(Transaction.transaction_id == transaction_id)
        .first()
    )
    if not transaction:
        raise HTTPException(status_code=404, detail="Transaction not found")
    return TransactionGet.model_validate(transaction)
