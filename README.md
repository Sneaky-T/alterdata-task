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

## Development cycle

- After a bit of research on fastAPI I've decided to choose it as a web framework, despite not actually being familiar with it (only used Django and Flask earlier). What made my mind was how flexible and lightweight it was compared to Django, also auto-docs feature really stole my heart. Pydantic schemas for data validation were also great. As for the database I've chosen PostgreSQL, since I wanted to demonstrate more professional approach. SQLite would be OK for this solution, especially when there is only one table currently, but I wanted the solution to be easily scalable and somewhat production-grade. I would also like to add that I'm more familiar with Django ORM, than with SQLAlchemy. Now, when the task is sent for review I consider my tech stack choice to partially be a mistake, because I didn't have enough expertise, and therefore time to compliment the solution. From another point of view I believe it demonstrates my ability to learn quickly.
- Database structure is one table only at the moment, which is enough to support current task requirements in my opinion, although if there was more data on customers and products, at least two more tables for each would be applicable and the customer_id, product_id being foreign keys in the transaction table, so there would be some actual relation then. Also at least for some part of the logs, there would be additional tables for them in the db. Especially that currently, there is no mechanism preventing growing log files to enormous sizes.
- Speaking of database there are some shortcomings in this matter code-wise. The first thing is creating/checking tables with a query instead of preparing migrations, other thing is no optimized databse pooling parameters.
- The logic layer is somewhat singular, certain functions are long, and should be split into separate methods more, so the code is easier to read. Also some scope of classes usage would be welcomed.
- The exception management in certain places could be more well-thought.
- The test coverage is a part that I'm most dissatisfied with because my decision to not use familiar stack, since I simply didn't have enough time to cover all scenarios, also had to ditch CSV upload test (that one really hurts), since it was giving me some problems, which again translated to significant time loss.
- Were I to continue working on the solution I would certainly expand the authentication mechanism for proper login and time-limited token management. Also the CSV import feature could be realised with multithreading parallel batch processing instead of doing it row by row (but it is realised as fastAPI background task, and memory efficient, since only one row at the time is loaded into system's memory).
-To conclude, despite some shortcomings, the general requirements for the task are met, including bonus ones. The whole codebase is clean, neatly organised and formatted with black.