from fastapi import (
    APIRouter,
    UploadFile,
    File,
    BackgroundTasks,
    Depends,
    Query,
)
from app.logic.transactions import (
    list_transactions,
    process_transactions,
    return_transaction,
)
from app.schemas.transaction import TransactionGet
from app.utils.file_utils import save_upload_to_tempfile
from app.db import Session, get_db
from typing import Optional
from uuid import UUID
import logging

logger = logging.getLogger(__name__)

transactions_router = APIRouter(prefix="/transactions", tags=["transactions"])


@transactions_router.post("/upload")
async def upload_transactions_csv(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
) -> dict[str, str]:
    logger.info(f"CSV upload started: {file.filename}")
    tmp_path = save_upload_to_tempfile(file)
    background_tasks.add_task(process_transactions, tmp_path)
    logger.info(f"CSV upload queued for processing: {file.filename}")
    return {"message": "File uploaded successfully."}


@transactions_router.get("/", response_model=list[TransactionGet])
def get_transactions(
    limit: int = Query(10, ge=1, le=100),
    offset: int = Query(0, ge=0),
    customer_id: Optional[UUID] = Query(None),
    product_id: Optional[UUID] = Query(None),
    db: Session = Depends(get_db),
) -> list[TransactionGet]:
    logger.info(
        f"Transaction list requested: limit={limit}, offset={offset}, customer_id={customer_id}, product_id={product_id}"
    )
    return list_transactions(limit, offset, customer_id, product_id, db)


@transactions_router.get("/{transaction_id}", response_model=TransactionGet)
def get_transaction(
    transaction_id: UUID,
    db: Session = Depends(get_db),
) -> TransactionGet:
    logger.info(f"Transaction detail requested: {transaction_id}")
    return return_transaction(transaction_id, db)
