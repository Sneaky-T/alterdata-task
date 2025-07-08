from fastapi import FastAPI
import logging


def setup_logging():
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(name)s - %(message)s",
    )
    logging.getLogger("sqlalchemy.engine").setLevel(logging.INFO)


setup_logging()

app = FastAPI()


@app.get("/")
def root():
    return {"message": "Welcome!"}
