from models import CustomerCreate, CustomerResponse, CustomerUpdate
from database import insert_customer , find_existing_customer, fetch_customer_by_id, fetch_all_customers, update_customer_with_history, connect_database, archive_customer_with_transaction
from exceptions import DuplicateConfirmationRequired, CustomerNotFoundError

def create_customer(
        customer: CustomerCreate,
        confirm_duplicate: bool = False
) -> CustomerResponse:
    connection = connect_database()
    try:
        connection.execute("BEGIN IMMEDIATE")

        existing_customers = find_existing_customer(
            connection,
            customer.email,
            customer.phone_number
        )

        if existing_customers and not confirm_duplicate:
            raise DuplicateConfirmationRequired(existing_customers)

        new_customer_id = insert_customer(
            connection,
            customer
        )
        customer_response = CustomerResponse(
                id = new_customer_id,
                full_name = customer.full_name,
                email = customer.email,
                phone_number = customer.phone_number,
                is_active = True
            )
        connection.commit()

    except Exception:
        connection.rollback()
        raise

    finally:
        connection.close()

    return customer_response

def get_customer_by_id(customer_id: int) -> CustomerResponse:

    customer_record = fetch_customer_by_id(customer_id)

    if customer_record is None:
        raise CustomerNotFoundError("Customer not found.")

    customer_response = CustomerResponse(
        id = customer_record["id"],
        full_name = customer_record["full_name"],
        email = customer_record["email"],
        phone_number = customer_record["phone_number"],
        is_active = customer_record["is_active"]
    )
    return customer_response

def get_all_customers() -> list[CustomerResponse]:

    customer_records = fetch_all_customers()

    customer_responses = []

    for record in customer_records:

        customer_response = CustomerResponse(
            id = record["id"],
            full_name = record["full_name"],
            email = record["email"],
            phone_number = record["phone_number"],
            is_active = record["is_active"]
        )
        customer_responses.append(customer_response)

    return customer_responses

def update_customer_details(
        customer_id: int,
        customer_update: CustomerUpdate,
        confirm_duplicate: bool = False
) -> CustomerResponse:

    existing_customer = get_customer_by_id(customer_id)

    updates = customer_update.model_dump(exclude_unset=True)

    changed_fields = {}

    for field_name, new_value in updates.items():

        if getattr(existing_customer, field_name)!= new_value:
            changed_fields[field_name] = new_value

    update_customer_with_history(
        customer_id,
        changed_fields,
        confirm_duplicate
    )

    customer_response = get_customer_by_id(
        customer_id
    )
    return customer_response

def archive_customer_details(customer_id: int):

    archive_customer_with_transaction(customer_id)

    return {"message": "Customer archived successfully."}