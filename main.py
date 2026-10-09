from fastapi import FastAPI, status, HTTPException
from exceptions import DuplicateConfirmationRequired
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
     status_code=status.HTTP_201_CREATED,
     responses={
           status.HTTP_409_CONFLICT:{
                 "description": "Possible duplicate customer found. Confirmation required."
           }
     }
)

def create_customer_endpoint(
      customer: CustomerCreate,
      confirm_duplicate: bool = False
):
          try:
                customer_response = create_customer(
                      customer,
                      confirm_duplicate
                )

                return customer_response

          except DuplicateConfirmationRequired as error:
                
                matching_customers = []

                for customer in error.existing_customers:
                      matching_customers.append({
                            "id": customer["id"],
                            "full_name": customer["full_name"],
                            "email": customer["email"],
                            "phone_number": customer["phone_number"]
                      })
                      
                raise HTTPException(
                      status_code=status.HTTP_409_CONFLICT,
                      detail={
                            "message": str(error),
                            "matching_customers": matching_customers
                      }
                )

          
          

