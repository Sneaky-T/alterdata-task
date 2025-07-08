from fastapi.testclient import TestClient
from app.main import app
import io
import time
import os
from app.db import SessionLocal
from app.models.transaction import Transaction


def test_root_endpoint():
    client = TestClient(app)
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "Welcome!"}


def test_overall_csv_upload_and_background_processing():
    from app.main import app

    client = TestClient(app)

    csv_content = (
        "transaction_id,customer_id,product_id,amount,currency,quantity,timestamp\n"
        "11111111-1111-1111-1111-111111111111,22222222-2222-2222-2222-222222222222,33333333-3333-3333-3333-333333333333,100.00,USD,1,2024-01-01T00:00:00\n"
        "21111111-1111-1111-1111-111111111111,22222222-2222-2222-2222-222222222222,33333333-3333-3333-3333-333333333333,200.00,EUR,2,2024-01-02T00:00:00\n"
        "31111111-1111-1111-1111-111111111111,22222222-2222-2222-2222-222222222222,33333333-3333-3333-3333-333333333333,300.00,PLN,3,2024-01-03T00:00:00\n"
        "41111111-1111-1111-1111-111111111111,22222222-2222-2222-2222-222222222222,33333333-3333-3333-3333-333333333333,400.00,USD,4,2024-01-04T00:00:00\n"
        "51111111-1111-1111-1111-111111111111,22222222-2222-2222-2222-222222222222,33333333-3333-3333-3333-333333333333,500.00,EUR,5,2024-01-05T00:00:00\n"
        "61111111-1111-1111-1111-111111111111,22222222-2222-2222-2222-222222222222,33333333-3333-3333-3333-333333333333,600.00,PLN,6,2024-01-06T00:00:00\n"
        "71111111-1111-1111-1111-111111111111,22222222-2222-2222-2222-222222222222,33333333-3333-3333-3333-333333333333,700.00,USD,7,2024-01-07T00:00:00\n"
        "a2111111-1111-1111-1111-111111111111,22222222-2222-2222-2222-222222222222,33333333-3333-3333-3333-333333333333,800.00,XXX,8,2024-01-08T00:00:00\n"  # invalid currency
        "b3111111-1111-1111-1111-111111111111,22222222-2222-2222-2222-222222222222,33333333-3333-3333-3333-333333333333,,USD,9,2024-01-09T00:00:00\n"  # missing 'amount' column
        "c4111111-1111-1111-1111-111111111111,22222222-2222-2222-2222-222222222222,33333333-3333-3333-3333-333333333333,notanumber,USD,10,2024-01-10T00:00:00\n"  # non-numeric amount
        "d5111111-1111-1111-1111-111111111111,22222222-2222-2222-2222-222222222222,33333333-3333-3333-3333-333333333333,999999999999999999999999.99,USD,11,2024-01-11T00:00:00\n"  # amount too large
        "11111111-1111-1111-1111-111111111111,22222222-2222-2222-2222-222222222222,33333333-3333-3333-3333-333333333333,1200.00,USD,12,2024-01-12T00:00:00\n"  # duplicate transaction_id
        "e6111111-1111-1111-1111-111111111111,22222222-2222-2222-2222-222222222222,33333333-3333-3333-3333-333333333333,1300.00,USD,13,2024-01-13T00:00:00,EXTRA\n"  # malformed row
    )
    files = {"file": ("test.csv", io.BytesIO(csv_content.encode("utf-8")), "text/csv")}

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
        assert "DataError" in log_content or "decimal.InvalidOperation" in log_content
        assert "IntegrityError" in log_content
        assert "Exception" in log_content or "TypeError" in log_content

    with SessionLocal() as session:
        count = session.query(Transaction).filter(Transaction.amount != None).count()
        assert count >= 7
