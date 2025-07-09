from app.db import Base
from sqlalchemy.engine import Engine

db_content = [
    # Customer 1, Product 1
    {
        "transaction_id": "11111111-1111-1111-1111-111111111111",
        "customer_id": "22222222-2222-2222-2222-222222222222",
        "product_id": "33333333-3333-3333-3333-333333333333",
        "amount": 100.0,
        "currency": "USD",
        "quantity": 1,
        "timestamp": "2024-01-01T00:00:00",
    },
    # Customer 2, Product 1
    {
        "transaction_id": "21111111-1111-1111-1111-111111111111",
        "customer_id": "22242222-2222-2222-2222-222222222222",
        "product_id": "33333333-3333-3333-3333-333333333333",
        "amount": 200.0,
        "currency": "EUR",
        "quantity": 2,
        "timestamp": "2024-01-02T00:00:00",
    },
    # Customer 3, Product 2
    {
        "transaction_id": "31111111-1111-1111-1111-111111111111",
        "customer_id": "22225222-2222-2222-2222-222222222222",
        "product_id": "33334444-3333-3333-3333-333333333333",
        "amount": 300.0,
        "currency": "PLN",
        "quantity": 3,
        "timestamp": "2024-01-03T00:00:00",
    },
    # Customer 1, Product 3
    {
        "transaction_id": "41111111-1111-1111-1111-111111111111",
        "customer_id": "22222222-2222-2222-2222-222222222222",
        "product_id": "33335555-3333-3333-3333-333333333333",
        "amount": 400.0,
        "currency": "USD",
        "quantity": 4,
        "timestamp": "2024-01-04T00:00:00",
    },
    # Customer 4, Product 1
    {
        "transaction_id": "51111111-1111-1111-1111-111111111111",
        "customer_id": "22262222-2222-2222-2222-222222222222",
        "product_id": "33333333-3333-3333-3333-333333333333",
        "amount": 500.0,
        "currency": "EUR",
        "quantity": 5,
        "timestamp": "2024-01-05T00:00:00",
    },
    # Customer 1, Product 4
    {
        "transaction_id": "61111111-1111-1111-1111-111111111111",
        "customer_id": "22222222-2222-2222-2222-222222222222",
        "product_id": "33336666-3333-3333-3333-333333333333",
        "amount": 600.0,
        "currency": "PLN",
        "quantity": 6,
        "timestamp": "2024-01-06T00:00:00",
    },
    # Customer 1, Product 5
    {
        "transaction_id": "71111111-1111-1111-1111-111111111111",
        "customer_id": "22222222-2222-2222-2222-222222222222",
        "product_id": "33337777-3333-3333-3333-333333333333",
        "amount": 700.0,
        "currency": "USD",
        "quantity": 7,
        "timestamp": "2024-01-07T00:00:00",
    },
]


def create_test_tables(engine: Engine) -> None:
    Base.metadata.create_all(bind=engine)
