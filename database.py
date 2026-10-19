# Import SQLite so we can create and use our database
import sqlite3


# Connect to the database
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
# ========== SPRINT 2 ADDED ==========

# Create the nutrition table
# This table stores food and calories for each user
cursor.execute("""
    CREATE TABLE IF NOT EXISTS nutrition (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        food_name TEXT NOT NULL,
        calories INTEGER NOT NULL,
        entry_date TEXT NOT NULL DEFAULT (date('now')),
        FOREIGN KEY (user_id) REFERENCES users(id)
    )
""")


# Create the workouts table
# This table stores workout information for each user
cursor.execute("""
    CREATE TABLE IF NOT EXISTS workouts (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        workout_type TEXT NOT NULL,
        duration INTEGER NOT NULL,
        entry_date TEXT NOT NULL DEFAULT (date('now')),
        FOREIGN KEY (user_id) REFERENCES users(id)
    )
""")


# Create the water table
# Stores how much water each user drinks
cursor.execute("""
    CREATE TABLE IF NOT EXISTS water (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        amount INTEGER NOT NULL,
        entry_date TEXT NOT NULL DEFAULT (date('now')),
        FOREIGN KEY (user_id) REFERENCES users(id)
    )
""")


# Create the sleep table
# Stores how many hours each user sleeps
cursor.execute("""
    CREATE TABLE IF NOT EXISTS sleep (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        hours REAL NOT NULL,
        entry_date TEXT NOT NULL DEFAULT (date('now')),
        FOREIGN KEY (user_id) REFERENCES users(id)
    )
""")


# ========== END SPRINT 2 ==========

# Save our changes
connection.commit()

# Close the database connection
connection.close()


print("Database created successfully.")