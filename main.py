from fastapi import FastAPI
from database import initialize_database
from contextlib import asynccontextmanager

@asynccontextmanager
async def lifespan(app:FastAPI):
     initialize_database()

     yield

app = FastAPI(lifespan=lifespan)

@app.get("/")

def home():
    return {"message": "OpsFlow is running"}

