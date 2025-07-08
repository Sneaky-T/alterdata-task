from fastapi import APIRouter, UploadFile, File, BackgroundTasks
from pydantic import ValidationError
from sqlalchemy.exc import DataError, IntegrityError, OperationalError
from app.db import SessionLocal
import csv
from app.schemas.transaction import TransactionPost
from app.models.transaction import Transaction
import logging
import tempfile
import shutil
import os


csv_handler = logging.FileHandler("logs/csv_import.log")
csv_handler.setFormatter(logging.Formatter("%(asctime)s [%(levelname)s] %(message)s"))
csv_logger = logging.getLogger("csv_logger")
csv_logger.propagate = False
csv_logger.addHandler(csv_handler)
csv_logger.setLevel(logging.INFO)

transactions_router = APIRouter(prefix="/transactions", tags=["transactions"])


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

            csv_logger.info(
                f"Processed {rows_processed} rows, {rows_failed} rows failed."
            )
    finally:
        try:
            os.remove(csv_file_tmp_path)
        except Exception as cleanup_err:
            csv_logger.error(
                f"Failed to remove temp file {csv_file_tmp_path}: {cleanup_err}"
            )


@transactions_router.post("/upload")
async def upload_transactions_csv(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
) -> dict[str, str]:
    with tempfile.NamedTemporaryFile(delete=False, suffix=".csv") as tmp:
        shutil.copyfileobj(file.file, tmp)
        tmp_path = tmp.name
    background_tasks.add_task(process_transactions, tmp_path)
    return {"message": "File uploaded successfully."}
