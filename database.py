import sqlite3
from models import CustomerCreate
from exceptions import CustomerNotFoundError

def connect_database():
    connection = sqlite3.connect(
        "opsflow.db"
    )
    connection.row_factory = sqlite3.Row
    connection.execute("PRAGMA foreign_keys = ON")
    return connection

def create_customers_table(connection):
    cursor = connection.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS customers (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        full_name TEXT NOT NULL,
        email TEXT NOT NULL,
        phone_number TEXT NOT NULL
        )
    """)
    connection.commit()

def create_customer_change_history_table(connection):
    cursor = connection.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS customer_change_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            customer_id INTEGER NOT NULL,
            field_name TEXT NOT NULL,
            old_value TEXT NOT NULL,
            new_value TEXT NOT NULL,
            changed_at TEXT NOT NULL,
            FOREIGN KEY (customer_id) REFERENCES customers(id)
        )
    """)    
    connection.commit()

def initialize_database():
    connection = connect_database()
    create_customers_table(connection)
    create_customer_change_history_table(connection)
    connection.close()

def insert_customer(customer: CustomerCreate) -> int:
    connection = connect_database()
    cursor = connection.cursor()

    cursor.execute("""
        INSERT INTO customers (
            full_name,
            email,
            phone_number
        )
        VALUES (?, ?, ?)
    """, (
        customer.full_name,
        customer.email,
        customer.phone_number
    ))    

    new_customer_id = cursor.lastrowid
    connection.commit()
    connection.close()
    return new_customer_id

def find_existing_customer(
        email: str | None,
        phone_number: str | None
):
    connection = connect_database()
    cursor = connection.cursor()

    cursor.execute(
        "SELECT * FROM customers WHERE email = ? OR phone_number = ?",
        (email, phone_number)
    )
    existing_customers = cursor.fetchall()
    connection.close()
    return existing_customers

def fetch_customer_by_id(customer_id: int):
    connection = connect_database()
    cursor = connection.cursor()

    cursor.execute(
        "SELECT * FROM customers WHERE id = ?",
        (customer_id,)
    )
    customer_record = cursor.fetchone()
    connection.close()
    return customer_record

def fetch_all_customers():
    connection = connect_database()
    cursor = connection.cursor()

    cursor.execute(
        "SELECT * FROM customers"
    )

    customer_records = cursor.fetchall()
    connection.close()
    return customer_records

def update_customer(
        connection,
        customer_id: int,
        updates: dict
):
    cursor = connection.cursor()

    cursor.execute("""
        UPDATE customers
        SET
           full_name = COALESCE(?, full_name),
           email = COALESCE(?, email),
           phone_number = COALESCE(?, phone_number)
        WHERE id = ?
        """, (
            updates.get("full_name"),
            updates.get("email"),
            updates.get("phone_number"),
            customer_id
        )   
    )
    
def insert_customer_change_history(
        connection,
        customer_id: int,
        field_name: str,
        old_value: str,
        new_value: str
):
    cursor = connection.cursor()

    cursor.execute("""
        INSERT INTO customer_change_history (
            customer_id,
            field_name,
            old_value,
            new_value,
            changed_at
        )
        VALUES (?, ?, ?, ?, CURRENT_TIMESTAMP)
    """,(
        customer_id,
        field_name,
        old_value,
        new_value
    ))

def update_customer_with_history(
        customer_id: int,
        updates: dict,
):    
    connection = connect_database()

    try:
        connection.execute("BEGIN IMMEDIATE")
        cursor = connection.cursor()

        cursor.execute(
            """
            SELECT id, full_name, email, phone_number
            FROM customers
            WHERE id = ?
            """,
            (customer_id,)
        )

        current_customer = cursor.fetchone()

        if current_customer is None:
            raise CustomerNotFoundError("Customer not found.")

        actual_changes = {}

        for field_name, new_value in updates.items():

            if current_customer[field_name] != new_value:

                actual_changes[field_name] = new_value

        if actual_changes:
            
            update_customer(
                connection,
                customer_id,
                actual_changes
            )
            
        for field_name, new_value in actual_changes.items():

            old_value = current_customer[field_name]

            insert_customer_change_history(
                connection,
                customer_id,
                field_name,
                old_value,
                new_value
            )
        connection.commit()    

    except Exception:
        connection.rollback()
        raise

    finally:
        connection.close()




    


