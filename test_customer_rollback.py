import sqlite3
from unittest.mock import patch

import database

test_connection = sqlite3.connect(":memory:")
database.create_customers_table(test_connection)