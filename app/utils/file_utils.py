import tempfile
import shutil
from fastapi import UploadFile


def save_upload_to_tempfile(file: UploadFile) -> str:
    with tempfile.NamedTemporaryFile(delete=False, suffix=".csv") as temp_csv_file:
        shutil.copyfileobj(file.file, temp_csv_file)
        return temp_csv_file.name
