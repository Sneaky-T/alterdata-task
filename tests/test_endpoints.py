import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.db import Base, get_db
from app.models import transaction
from app.models.transaction import Transaction
from app.utils.test_utils import db_content, dirty_csv_content, create_test_tables
from app.main import app
import io
import os
import time
from decimal import Decimal

SQLALCHEMY_DATABASE_URL = (
    "postgresql+psycopg2://admin:secret@localhost:5433/transactions_test_db"
)


@pytest.fixture(scope="function")
def db_session():
    engine = create_engine(SQLALCHEMY_DATABASE_URL)

    create_test_tables(engine)

    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    session = TestingSessionLocal()

    for record in db_content:
        session.add(Transaction(**record))
    session.commit()

    yield session

    session.close()

    Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def client(db_session):
    def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db

    return TestClient(app)


def test_root_endpoint(client):
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "Welcome!"}


class TestTransactionsEndpoints:
    def test_list_transactions(self, client):
        response = client.get("/transactions")
        assert response.status_code == 200

        data = response.json()
        assert isinstance(data, list)
        assert len(data) == 7
        for transaction in data:
            assert len(transaction) == 8

    def test_transaction_detail(self, client):
        transaction_id = "11111111-1111-1111-1111-111111111111"

        response = client.get(f"/transactions/{transaction_id}")
        assert response.status_code == 200

        data = response.json()
        assert data["transaction_id"] == transaction_id
        assert len(data) == 8


class TestCsvUpload:
    def test_csv_upload_comprehensive(self, client):
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
            assert log_content.count("ValidationError") >= 3
            assert (
                "DataError" in log_content or "decimal.InvalidOperation" in log_content
            )
            assert "IntegrityError" in log_content
            assert "Exception" in log_content or "TypeError" in log_content


class TestCustomerSummaryEndpoints:
    def test_customer_summary(self, client):
        customer_id = "22222222-2222-2222-2222-222222222222"

        response = client.get(f"/customer-summary/{customer_id}")
        assert response.status_code == 200

        data = response.json()
        assert Decimal(data["total_amount_in_PLN"]) == Decimal("5400.00")
        assert data["unique_product_count"] == 4
        assert data["last_transaction_date"] == "2024-01-07T00:00:00"

    def test_customer_summary_with_date_limits(self, client):
        customer_id = "22222222-2222-2222-2222-222222222222"

        response = client.get(
            f"/customer-summary/{customer_id}?end_date=2024-01-04T23:59:59"
        )
        assert response.status_code == 200

        data = response.json()
        assert Decimal(data["total_amount_in_PLN"]) == Decimal("2000.00")
        assert data["unique_product_count"] == 2
        assert data["last_transaction_date"] == "2024-01-04T00:00:00"
