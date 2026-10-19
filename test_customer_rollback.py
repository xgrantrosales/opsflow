import sqlite3
import tempfile
from unittest.mock import patch
import database
from pathlib import Path

temporary_directory = tempfile.TemporaryDirectory()
test_db_path = Path(temporary_directory.name) / "test_opsflow.db"

test_connection = sqlite3.connect(test_db_path)
test_connection.row_factory = sqlite3.Row

database.create_customers_table(test_connection)

test_connection.execute("""
    INSERT INTO customers (
        full_name,
        email,
        phone_number
    )
    VALUES (?, ?, ?)
    """, (
        "Jane Test",
        "jane.test@example.com",
        "09171111111"
    )
)
test_connection.commit()
test_connection.close()

def connect_test_database():
    connection = sqlite3.connect(test_db_path)
    connection.row_factory = sqlite3.Row
    connection.execute("PRAGMA foreign_keys = ON")
    return connection

def simulate_history_failure(*args, **kwargs):
    raise RuntimeError("Simulated history insertion failure")

with patch("database.connect_database", new=connect_test_database):
    with patch(
        "database.insert_customer_change_history",
        new=simulate_history_failure
    ):
        try:
            
            database.update_customer_with_history(
                1,
                {"phone_number": "09172222222"}
            )

        except RuntimeError as error:
            print(f"Expected test error: {error}")  

        else:
            raise AssertionError("Expected history insertion failure did not occur")      

print(database.connect_database is connect_test_database)    
verification_connection = sqlite3.connect(test_db_path)

cursor = verification_connection.execute(
    """
    SELECT phone_number
    FROM customers
    WHERE id = ?
    """,
    (1,)
)

phone_number = cursor.fetchone()[0]

print(f"Phone number after rollback: {phone_number}")

assert phone_number == "09171111111"

verification_connection.close()

temporary_directory.cleanup()







