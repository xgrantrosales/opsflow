import sqlite3
from models import CustomerCreate

def connect_database():
    connection = sqlite3.connect(
        "opsflow.db"
    )
    connection.row_factory = sqlite3.Row
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

def initialize_database():
    connection = connect_database()
    create_customers_table(connection)
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