from models import CustomerCreate, CustomerResponse
from database import insert_customer , find_existing_customer, fetch_customer_by_id
from exceptions import DuplicateConfirmationRequired, CustomerNotFoundError

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

def get_customer_by_id(customer_id: int) -> CustomerResponse:

    customer_record = fetch_customer_by_id(customer_id)

    if customer_record is None:
        raise CustomerNotFoundError("Customer not found.")

    customer_response = CustomerResponse(
        id = customer_record["id"],
        full_name = customer_record["full_name"],
        email = customer_record["email"],
        phone_number = customer_record["phone_number"]
    )

    return customer_response



