from models import CustomerCreate, CustomerResponse
from database import insert_customer , find_existing_customer
from exceptions import DuplicateConfirmationRequired

def create_customer(
        customer: CustomerCreate,
        confirm_duplicate: bool = False
) -> CustomerResponse:

    existing_customers = find_existing_customer(
        customer.email,
        customer.phone_number
    )

    if existing_customers and not confirm_duplicate:
        raise DuplicateConfirmationRequired(existing_customers)

    new_customer_id = insert_customer(customer)

    customer_response = CustomerResponse(
        id = new_customer_id,
        full_name = customer.full_name,
        email = customer.email,
        phone_number = customer.phone_number
    )

    return customer_response



