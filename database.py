# Import SQLite so we can create and use our database
import sqlite3

# Conntect to the database
# If the database does not exist, SQLite will create it
connection = sqlite3.connect("health_wellness.db")

# Cursor lets us run SQL commands
cursor = connection.cursor()

# Create the users table
# This table stores the accounts for our application
cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        email TEXT NOT NULL UNIQUE,
        password TEXT NOT NULL
    )
""")

# Save our changes
connection.commit()

# Close the database connection
connection.close()

print("Database created successfully")