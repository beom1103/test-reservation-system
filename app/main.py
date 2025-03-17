from fastapi import FastAPI
import os


app = FastAPI(
    title="Test Reservation System",
    version="1.0.0",
    docs_url="/api-docs",
)


@app.get("/")
async def root():
    db_url = os.getenv("DATABASE_URL", "Not Found")

    return {"message": "Hello, FastAPI with Poetry & Docker!", "db_url": db_url}
