from fastapi.testclient import TestClient
from app.main import app
import io
import time
import os
from app.db import SessionLocal
from app.models.transaction import Transaction
from sqlalchemy import text
from app.utils.test_utils import db_content, dirty_csv_content


def test_root_endpoint():
    client = TestClient(app)
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "Welcome!"}


class TestTransactionsEndpoints:
    @classmethod
    def setup_class(cls):
        cls.client = TestClient(app)

        cls.session = SessionLocal()
        cls.session.execute(text("DELETE FROM transactions"))
        cls.session.commit()

        for record in db_content:
            cls.session.add(Transaction(**record))
        cls.session.commit()

    def test_list_transactions(self):
        response = self.client.get("/transactions")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        for transaction in data:
            print(transaction)
        assert len(data) == 7
        for transaction in data:
            assert len(transaction) == 8

    def test_transaction_detail(self):
        transaction_id = "11111111-1111-1111-1111-111111111111"
        response = self.client.get(f"/transactions/{transaction_id}")
        assert response.status_code == 200
        data = response.json()
        assert data["transaction_id"] == transaction_id
        assert len(data) == 8


class TestCsvUpload:
    def test_csv_upload_comprehensive(self):
        client = TestClient(app)

        files = {
            "file": (
                "test.csv",
                io.BytesIO(dirty_csv_content.encode("utf-8")),
                "text/csv",
            )
        }

        response = client.post("/transactions/upload", files=files)
        assert response.status_code == 200
        assert response.json() == {"message": "File uploaded successfully."}

        time.sleep(1)  # wait for background task to finish

        log_path = "logs/csv_import.log"
        assert os.path.exists(log_path)
        with open(log_path, "r", encoding="utf-8") as log_file:
            log_content = log_file.read()
            assert "Processed 13 rows, 6 rows failed" in log_content
            assert (
                log_content.count("ValidationError") >= 3
            )  # pydantic catches some errors as ValidationError
            assert (
                "DataError" in log_content or "decimal.InvalidOperation" in log_content
            )
            assert "IntegrityError" in log_content
            assert "Exception" in log_content or "TypeError" in log_content

        with SessionLocal() as session:
            count = (
                session.query(Transaction).filter(Transaction.amount != None).count()
            )
            assert count >= 7
