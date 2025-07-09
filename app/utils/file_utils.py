import tempfile
import shutil
from fastapi import UploadFile, HTTPException
import logging

logger = logging.getLogger(__name__)


def save_upload_to_tempfile(file: UploadFile) -> str:
    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".csv") as temp_csv_file:
            shutil.copyfileobj(file.file, temp_csv_file)
            logger.info(f"File uploaded successfully: {temp_csv_file.name}")
            return temp_csv_file.name
    except (OSError, shutil.Error) as e:
        logger.error(f"File upload error: {type(e).__name__}: {e}")
        raise HTTPException(
            status_code=500, detail=f"File upload error: {type(e).__name__}: {e}"
        )
    except Exception as e:
        logger.exception("Unexpected error during file upload")
        raise HTTPException(
            status_code=500, detail=f"Unexpected error: {type(e).__name__}: {e}"
        )
