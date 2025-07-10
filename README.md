# Transaction Processing API

A FastAPI-based backend system for processing and aggregating transaction data with PostgreSQL database support.

## Features

- CSV file upload and validation
- Transaction data storage and querying
- Customer and product summary reports
- Date range filtering for the reports
- Currency conversion support
- API key authentication
- Test suite

## Quick Start with Docker

### Prerequisites
- Docker
- Docker Compose

### Setup

1. Clone the repository:
```bash
git clone <repository-url>
cd alterdata-task
```

2. Start the complete infrastructure:
```bash
docker-compose up -d
```

This will start:
- PostgreSQL database (port 5432)
- Test PostgreSQL database (port 5433)
- FastAPI application (port 8000)

3. Wait for all services to be healthy:
```bash
docker-compose ps
```

4. Access the API:
- API Base URL: http://localhost:8000
- API Documentation: http://localhost:8000/docs
- Health Check: http://localhost:8000/

## API Usage

### Authentication
All endpoints (except for root) require an API key in the header:
```
x-api-key: secret-key
```

### Endpoints & Query Parameters

#### Transactions
- `GET /transactions` - List all transactions
  - **Query Parameters:**
    - `customer_id` (UUID): Filter by customer
    - `product_id` (UUID): Filter by product
    - `limit` (int): Page size (min: 1, max: 100)
    - `offset` (int): Offset (how many records to skip, min: 0)
- `GET /transactions/{transaction_id}` - Get specific transaction (no additional query params)
- `POST /transactions/upload` - Upload CSV file (no additional query params)

#### Reports
- `GET /reports/customer-summary/{customer_id}` - Customer summary report
  - **Query Parameters:**
    - `start_date` (ISO 8601): Filter transactions from this date
    - `end_date` (ISO 8601): Filter transactions up to this date
- `GET /reports/product-summary/{product_id}` - Product summary report
  - **Query Parameters:**
    - `start_date` (ISO 8601): Filter transactions from this date
    - `end_date` (ISO 8601): Filter transactions up to this date

## Environment Variables

### Local Development
Create a `.env` file in the project root:
```
API_KEY=secret-key
DATABASE_URL=postgresql+psycopg2://admin:secret@localhost:5432/transactions_db
TEST_DATABASE_URL=postgresql+psycopg2://admin:secret@localhost:5433/transactions_test_db
LOG_LEVEL=INFO
HOST=0.0.0.0
PORT=8000
```

### Docker Compose
Environment variables are set in `docker-compose.yml` for the `app` service:
- `DATABASE_URL=postgresql+psycopg2://admin:secret@db:5432/transactions_db`
- `TEST_DATABASE_URL=postgresql+psycopg2://admin:secret@test_db:5432/transactions_test_db`
- `API_KEY=secret-key`
- `LOG_LEVEL=INFO`
- `HOST=0.0.0.0`
- `PORT=8000`

## Development

### Running Tests
```bash
# Run tests in Docker
docker-compose exec app python -m pytest

# Run specific test file
docker-compose exec app python -m pytest tests/test_endpoints.py
```

## Architecture

- **FastAPI** - Web framework
- **SQLAlchemy** - ORM
- **PostgreSQL** - Database
- **Pydantic** - Data validation
- **Pytest** - Testing framework

## Docker Services

- `app` - FastAPI application
- `db` - Main PostgreSQL database
- `test_db` - Test PostgreSQL database

## TODO Development decisions and compromises