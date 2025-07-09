import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from app.db import Base, get_db
from app.models import transaction
from app.models.transaction import Transaction
from tests.test_utils import db_content, create_test_tables
from app.main import app
import os
from decimal import Decimal
from typing import Generator, Any

TEST_DATABASE_URL = os.getenv(
    "TEST_DATABASE_URL",
    "postgresql+psycopg2://admin:secret@localhost:5433/transactions_test_db",
)


@pytest.fixture(scope="function")
def db_session() -> Generator[Session, None, None]:
    engine = create_engine(TEST_DATABASE_URL)

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
def client(db_session: Session) -> TestClient:
    def override_get_db() -> Generator[Session, None, None]:
        yield db_session

    app.dependency_overrides[get_db] = override_get_db

    class APIKeyTestClient(TestClient):
        def request(self, method: str, url: str, **kwargs) -> Any:
            headers = kwargs.pop("headers", {}) or {}
            headers.setdefault("x-api-key", "secret-key")
            return super().request(method, url, headers=headers, **kwargs)

    return APIKeyTestClient(app)


def test_root_endpoint(client: TestClient) -> None:
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "Welcome!"}


def test_auth_wrong_key(client: TestClient) -> None:
    response = client.get("/transactions", headers={"x-api-key": "wrong-key"})
    assert response.status_code == 401

    assert response.json()["detail"] == "Invalid or missing API Key."


class TestTransactionsEndpoints:
    def test_list_transactions(self, client: TestClient) -> None:
        response = client.get("/transactions")
        assert response.status_code == 200

        data = response.json()
        assert isinstance(data, list)
        assert len(data) == 7
        for transaction in data:
            assert len(transaction) == 8

    def test_transaction_detail(self, client: TestClient) -> None:
        transaction_id = "11111111-1111-1111-1111-111111111111"

        response = client.get(f"/transactions/{transaction_id}")
        assert response.status_code == 200

        data = response.json()
        assert data["transaction_id"] == transaction_id
        assert len(data) == 8


class TestCustomerSummaryEndpoints:
    def test_customer_summary(self, client: TestClient) -> None:
        customer_id = "22222222-2222-2222-2222-222222222222"
        response = client.get(f"/reports/customer-summary/{customer_id}")
        assert response.status_code == 200
        data = response.json()
        assert Decimal(data["total_amount_in_PLN"]) == Decimal("5400.00")
        assert data["unique_product_count"] == 4
        assert data["last_transaction_date"] == "2024-01-07T00:00:00"

    def test_customer_summary_with_date_limits(self, client: TestClient) -> None:
        customer_id = "22222222-2222-2222-2222-222222222222"
        response = client.get(
            f"/reports/customer-summary/{customer_id}?end_date=2024-01-04T23:59:59"
        )
        assert response.status_code == 200
        data = response.json()
        assert Decimal(data["total_amount_in_PLN"]) == Decimal("2000.00")
        assert data["unique_product_count"] == 2
        assert data["last_transaction_date"] == "2024-01-04T00:00:00"


class TestProductSummaryEndpoints:
    def test_product_summary(self, client: TestClient) -> None:
        product_id = "33333333-3333-3333-3333-333333333333"

        response = client.get(f"/reports/product-summary/{product_id}")
        assert response.status_code == 200

        data = response.json()
        assert data["total_quantity"] == 8
        assert Decimal(data["total_amount_in_PLN"]) == Decimal("3410.00")
        assert data["unique_customer_count"] == 3

    def test_product_summary_with_date_limits(self, client: TestClient) -> None:
        product_id = "33333333-3333-3333-3333-333333333333"

        response = client.get(
            f"/reports/product-summary/{product_id}?end_date=2024-01-02T23:59:59"
        )
        assert response.status_code == 200

        data = response.json()
        assert data["total_quantity"] == 3
        assert Decimal(data["total_amount_in_PLN"]) == Decimal("1260.00")
        assert data["unique_customer_count"] == 2
