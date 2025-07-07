from app.db import engine
from sqlalchemy.exc import OperationalError
from sqlalchemy import text


def test_database_connection():
    try:
        with engine.connect() as connection:
            result = connection.execute(text("SELECT 1;"))
            assert result.scalar() == 1
    except OperationalError:
        assert False, "Database connection failed!"
