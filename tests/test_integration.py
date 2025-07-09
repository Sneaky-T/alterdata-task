import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from app.db import Base, get_db
from app.models.transaction import Transaction
from tests.test_utils import db_content, create_test_tables
from app.main import app
import os
from collections.abc import Generator

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
    def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db

    class APIKeyTestClient(TestClient):
        def request(self, method: str, url: str, **kwargs):
            headers = kwargs.pop("headers", {}) or {}
            headers.setdefault("x-api-key", "secret-key")
            return super().request(method, url, headers=headers, **kwargs)

    return APIKeyTestClient(app)


class TestErrorHandlingIntegration:
    def test_nonexistent_transaction(self, client: TestClient):
        fake_id = "99999999-9999-9999-9999-999999999999"

        response = client.get(
            f"/transactions/{fake_id}", headers={"x-api-key": "secret-key"}
        )
        assert response.status_code == 404

        assert "Transaction not found" in response.json()["detail"]

    def test_nonexistent_customer_report(self, client: TestClient):
        fake_id = "99999999-9999-9999-9999-999999999999"

        response = client.get(
            f"/reports/customer-summary/{fake_id}", headers={"x-api-key": "secret-key"}
        )
        assert response.status_code == 404

        assert "Customer not found" in response.json()["detail"]

    def test_nonexistent_product_report(self, client: TestClient):
        fake_id = "99999999-9999-9999-9999-999999999999"

        response = client.get(
            f"/reports/product-summary/{fake_id}", headers={"x-api-key": "secret-key"}
        )
        assert response.status_code == 404

        assert "Product not found" in response.json()["detail"]
