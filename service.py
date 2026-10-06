from models import CustomerCreate, CustomerResponse
from database import insert_customer

def create_customer(customer: CustomerCreate) -> CustomerResponse:

    new_customer_id = insert_customer(customer)

    customer_response = CustomerResponse(
        id = new_customer_id,
        full_name = customer.full_name,
        email = customer.email,
        phone_number = customer.phone_number
    )

    return customer_response


