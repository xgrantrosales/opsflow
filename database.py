import sqlite3
from models import CustomerCreate
from exceptions import CustomerNotFoundError, DuplicateConfirmationRequired , CustomerAlreadyArchivedError, CustomerAlreadyActiveError

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
        phone_number TEXT NOT NULL,
        is_active INTEGER NOT NULL DEFAULT 1
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

def migrate_customer_archiving(connection):
    cursor = connection.cursor()

    cursor.execute("PRAGMA table_info(customers)")
    columns = cursor.fetchall()

    column_names = []

    for column in columns:
        column_names.append(column["name"])

    if "is_active" not in column_names:
        cursor.execute("""
            ALTER TABLE customers
            ADD COLUMN is_active INTEGER NOT NULL DEFAULT 1
        """)

        connection.commit()

def initialize_database():
    connection = connect_database()
    create_customers_table(connection)
    migrate_customer_archiving(connection)
    create_customer_change_history_table(connection)
    connection.close()

def insert_customer(
        connection,
        customer: CustomerCreate
) -> int:
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
    return new_customer_id

def find_existing_customer(
        connection,
        email: str | None,
        phone_number: str | None
):
    cursor = connection.cursor()

    cursor.execute(
        "SELECT * FROM customers WHERE email = ? OR phone_number = ?",
        (email, phone_number)
    )
    existing_customers = cursor.fetchall()
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
        confirm_duplicate: bool = False
):
    connection = connect_database()

    try:
        connection.execute("BEGIN IMMEDIATE")
        cursor = connection.cursor()

        cursor.execute(
            """
            SELECT id, full_name, email, phone_number, is_active
            FROM customers
            WHERE id = ?
            """,
            (customer_id,)
        )

        current_customer = cursor.fetchone()

        if current_customer is None:
            raise CustomerNotFoundError("Customer not found.")

        if current_customer["is_active"] == 0:
            raise CustomerAlreadyArchivedError(
                "Cannot update an archived customer."
            )

        actual_changes = {}

        for field_name, new_value in updates.items():

            if current_customer[field_name] != new_value:

                actual_changes[field_name] = new_value

        if "email" in actual_changes or "phone_number" in actual_changes:

            existing_customers = find_existing_customer(
                connection,
                actual_changes.get("email"),
                actual_changes.get("phone_number")
            )

            other_customers = []

            for customer in existing_customers:
                if customer["id"] != customer_id:
                    other_customers.append(customer)

            if other_customers and not confirm_duplicate:
                raise DuplicateConfirmationRequired(other_customers)

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

def archive_customer_with_transaction(customer_id: int):
    connection = connect_database()

    try:
        connection.execute("BEGIN IMMEDIATE")
        cursor = connection.cursor()

        cursor.execute("""
            SELECT id, is_active
            FROM customers
            WHERE id = ?
        """, (customer_id,))

        current_customer = cursor.fetchone()

        if current_customer is None:
            raise CustomerNotFoundError("Customer not found.")

        if current_customer["is_active"] == 0:
            raise CustomerAlreadyArchivedError("Customer is already archived.")

        rows_affected = archive_customer(
            connection,
            customer_id
        )
        if rows_affected != 1:
            raise RuntimeError("Customer archiving failed.")

        connection.commit()

    except Exception:
        connection.rollback()
        raise

    finally:
        connection.close()

def archive_customer(
        connection,
        customer_id: int
):
    cursor = connection.cursor()

    cursor.execute("""
        UPDATE customers
        SET is_active = 0
        WHERE id = ? AND is_active = 1
    """, (customer_id,))

    return cursor.rowcount

def reactivate_customer(
        connection,
        customer_id: int
):
    cursor = connection.cursor()

    cursor.execute("""
        UPDATE customers
        SET is_active = 1
        WHERE id = ? AND is_active = 0
    """, (customer_id,))

    return cursor.rowcount

def reactivate_customer_with_transaction(
        customer_id: int
):
    connection = connect_database()

    try:
        connection.execute("BEGIN IMMEDIATE")
        cursor = connection.cursor()

        cursor.execute("""
            SELECT id, is_active
            FROM customers
            WHERE id = ?
        """, (customer_id,))

        current_customer = cursor.fetchone()

        if current_customer is None:
            raise CustomerNotFoundError("Customer not found.")

        if current_customer["is_active"] == 1:
            raise CustomerAlreadyActiveError(
                "Customer is already active."
            )

        rows_affected = reactivate_customer(
            connection,
            customer_id
        )

        if rows_affected != 1:
            raise RuntimeError("Customer reactivation failed.")

        connection.commit()

    except Exception:
        connection.rollback()
        raise

    finally:
        connection.close()






