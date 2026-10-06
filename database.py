import sqlite3

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

    