from fastapi import FastAPI, status, HTTPException
from exceptions import DuplicateConfirmationRequired, CustomerNotFoundError, CustomerAlreadyArchivedError, CustomerAlreadyActiveError
from database import initialize_database
from contextlib import asynccontextmanager
from models import CustomerCreate, CustomerResponse, CustomerUpdate, CustomerArchiveResponse
from service import create_customer, get_customer_by_id, get_all_customers, update_customer_details, archive_customer_details, reactivate_customer_details

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

@app.get(
      "/customers/{customer_id}",
      response_model=CustomerResponse,
      status_code=status.HTTP_200_OK,
      responses={
            status.HTTP_404_NOT_FOUND: {
                  "description": "Customer not found."
            }
      }

)

def get_customer_by_id_endpoint(customer_id: int):

      try:
            customer_response = get_customer_by_id(customer_id)
            return customer_response

      except CustomerNotFoundError as error:
            raise HTTPException(
                  status_code=status.HTTP_404_NOT_FOUND,
                  detail=str(error)
            )

@app.get(
      "/customers",
      response_model=list[CustomerResponse],
      status_code=status.HTTP_200_OK
)

def get_all_customers_endpoint():

      customer_response = get_all_customers()

      return customer_response

@app.patch(
      "/customers/{customer_id}",
      response_model=CustomerResponse,
      status_code=status.HTTP_200_OK,
      responses={
            status.HTTP_404_NOT_FOUND: {
                  "description": "Customer not found."
            },
            status.HTTP_409_CONFLICT: {
                  "description": "Possible duplicate customer found. Confirmation required."
            }
      }
)

def update_customer_endpoint(
      customer_id: int,
      customer_update: CustomerUpdate,
      confirm_duplicate: bool = False
):
      try:
            customer_response = update_customer_details(
                  customer_id,
                  customer_update,
                  confirm_duplicate
            )
            return customer_response

      except CustomerNotFoundError as error:
            raise HTTPException(
                  status_code=status.HTTP_404_NOT_FOUND,
                  detail=str(error)
            )
      except CustomerAlreadyArchivedError as error:
            raise HTTPException(
                  status_code=status.HTTP_409_CONFLICT,
                  detail=str(error)
            )
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

@app.patch(
      "/customers/{customer_id}/archive",
      response_model=CustomerArchiveResponse,
      status_code=status.HTTP_200_OK,
      responses={
            status.HTTP_404_NOT_FOUND: {
                  "description": "Customer not found."
            },
            status.HTTP_409_CONFLICT: {
                  "description": "Customer is already archived."
            }
      }
)

def archive_customer_endpoint(customer_id: int):

      try:
            result = archive_customer_details(customer_id)
            return result

      except CustomerNotFoundError as error:
            raise HTTPException(
                  status_code=status.HTTP_404_NOT_FOUND,
                  detail=str(error)
            )

      except CustomerAlreadyArchivedError as error:
            raise HTTPException(
                  status_code=status.HTTP_409_CONFLICT,
                  detail=str(error)
            )

@app.patch(
      "/customers/{customer_id}/reactivate",
      response_model=CustomerArchiveResponse,
      status_code=status.HTTP_200_OK,
      responses={
            status.HTTP_404_NOT_FOUND: {
                  "description": "Customer not found."
            },
            status.HTTP_409_CONFLICT: {
                  "description": "Customer is already active."
            }
      }
)

def reactivate_customer_endpoint(customer_id: int):

      try:
            result = reactivate_customer_details(customer_id)
            return result

      except CustomerNotFoundError as error:
            raise HTTPException(
                  status_code=status.HTTP_404_NOT_FOUND,
                  detail=str(error)
            )

      except CustomerAlreadyActiveError as error:
            raise HTTPException(
                  status_code=status.HTTP_409_CONFLICT,
                  detail=str(error)
            )

