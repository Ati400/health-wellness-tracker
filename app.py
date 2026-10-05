# Import the Flask tools we need
from flask import Flask, request, redirect, session, send_from_directory

# Import SQLite so we can use our database
import sqlite3

# Create our Flask application
app = Flask(__name__)

# Flask needs a secret key to use sessions
# Sessions help us remember who is logged in
app.secret_key = "health_wellness_project"

# -----------------------------
# HOME / LOGIN PAGE
# -----------------------------

@app.route("/")
def home():

    # Show the login page
    return send_from_directory(".", "index.html")

# -----------------------------
# REGISTER PAGE
# -----------------------------

@app.route("/register")
def register_page():

    # Show the create account page
    return send_from_directory(".", "register.html")

# -----------------------------
# CREATE ACCOUNT
# -----------------------------

@app.route("/create-account", methods=["POST"])
def create_account():

    # Get the information from the registration form
    name = request.form.get("name")
    email = request.form.get("email")
    password = request.form.get("password")

    # Make sure all fields were entered
    if not name or not email or not password:
        return redirect("/register?error=missing")
    
    # Make sure the password is at least 8 characters
    if len(password) < 8:
        return redirect("/register?error=password")
        
    # Connect to our database
    connection = sqlite3.connect("health_wellness.db")
    cursor = connection.cursor()

    try:

        # Add the new user to the users table
        cursor.execute(
            """
            INSERT INTO users (name, email, password)
            VALUES (?, ?, ?)
            """,
            (name, email, password)
        )

        # Save the new account
        connection.commit()

    except sqlite3.IntegrityError:

        # Close the database
        connection.close()

        # Return to registration page
        # This usually means the email already exists
        return redirect("/register?error=email")

    # Close the database
    connection.close()

    # Send the user to the login page
    return redirect("/?created=1")

# -----------------------------
# LOGIN
# -----------------------------

@app.route("/login", methods=["POST"])
def login():

    # Get the information from the login form
    email = request.form.get("email")
    password = request.form.get("password")

    # Make sure both fields were received
    if not email or not password:
        return redirect("/?error=1")

    # Connect to our database
    connection = sqlite3.connect("health_wellness.db")
    cursor = connection.cursor()

    # Look for an account with this email and password
    cursor.execute(
        """
        SELECT id, name, email
        FROM users
        WHERE email = ? AND password = ?
        """,
        (email, password)
    )

    # Get the account if it exists
    user = cursor.fetchone()

    # Close the database
    connection.close()


    # Check if the account was found
    if user:

        # Save information about the logged-in user
        session["user_id"] = user[0]
        session["user_name"] = user[1]

        # Go to the dashboard
        return redirect("/dashboard")


    # If login information was incorrect,
    # return to the login page
    return redirect("/?error=1")

# -----------------------------
# DASHBOARD
# -----------------------------

@app.route("/dashboard")
def dashboard():

    # Make sure the user is logged in
    if "user_id" not in session:
        return redirect("/")

    # Show the dashboard
    return send_from_directory(".", "dashboard.html")
