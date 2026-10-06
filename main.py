from fastapi import FastAPI, status, HTTPException
from database import initialize_database
from contextlib import asynccontextmanager
from models import CustomerCreate, CustomerResponse
from service import create_customer

@asynccontextmanager
async def lifespan(app:FastAPI):
     initialize_database()

     yield

app = FastAPI(lifespan=lifespan)

@app.get("/")

def home():
    return {"message": "OpsFlow is running"}

@app.post(
     "/customers",
     response_model=CustomerResponse,
     status_code=status.HTTP_201_CREATED
)

def create_customer_endpoint(customer: CustomerCreate):
          
          customer_response = create_customer(customer)

          return customer_response

          
          

