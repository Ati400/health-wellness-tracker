# Import the Flask tools we need
from flask import Flask, request, redirect, session, send_from_directory

# Password security and reset
from werkzeug.security import generate_password_hash, check_password_hash
from itsdangerous import URLSafeTimedSerializer, BadSignature, SignatureExpired

# Sprint 2 - Read HTML files and track dates
from pathlib import Path
from datetime import date
# Import SQLite so we can use our database
import sqlite3

# Create our Flask application
app = Flask(__name__)

# Flask needs a secret key to use sessions
# Sessions help us remember who is logged in
app.secret_key = "health_wellness_project"

# Create the users table if it does not already exist
def init_database():
    connection = sqlite3.connect("health_wellness.db")
    cursor = connection.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT NOT NULL UNIQUE,
            password TEXT NOT NULL
        )
    """)

    connection.commit()
    connection.close()
# Sprint 2 - Database connection for tracking
def tracking_connection():
    connection = sqlite3.connect("health_wellness.db")
    connection.row_factory = sqlite3.Row
    return connection
    
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

# -----------------------------
# PROFILE
# -----------------------------

@app.route("/profile")
def profile():

    # Make sure the user is logged in
    if "user_id" not in session:
        return redirect("/")

    # Show the profile page
    return send_from_directory(".", "profile.html")

# -----------------------------
# USER INFORMATION
# -----------------------------

@app.route("/user")
def get_user():

    # Make sure someone is logged in
    if "user_id" not in session:
        return {
            "name": "",
            "email": ""
        }

    # Get the logged-in user's ID
    user_id = session["user_id"]

    # Connect to the database
    connection = sqlite3.connect("health_wellness.db")
    cursor = connection.cursor()

    # Find the logged-in user's information
    cursor.execute(
        """
        SELECT name, email
        FROM users
        WHERE id = ?
        """,
        (user_id,)
    )

    user = cursor.fetchone()

    # Close the database
    connection.close()


    # Return the user's information
    if user:
        return {
            "name": user[0],
            "email": user[1]
        }

    return {
        "name": "",
        "email": ""
    }

# -----------------------------
# LOGOUT
# -----------------------------

@app.route("/logout")
def logout():

    # Remove the user's login information
    session.clear()

    # Return to the login page
    return redirect("/")

# -----------------------------
# CSS FILE
# -----------------------------

@app.route("/style.css")
def style():

    return send_from_directory(".", "style.css")


# -----------------------------
# JAVASCRIPT FILE
# -----------------------------

@app.route("/script.js")
def script():

    return send_from_directory(".", "script.js")

# -----------------------------
# SPRINT 2 - NUTRITION TRACKING
# -----------------------------

@app.route("/nutrition", methods=["GET", "POST"])
def nutrition():

    # Make sure the user is logged in
    if "user_id" not in session:
        return redirect("/")

    connection = tracking_connection()
    error = None

    # Save food when the form is submitted
    if request.method == "POST":

        food_name = request.form.get("food_name", "").strip()

        try:
            calories = int(request.form.get("calories", ""))

            # Check if the information is valid
            if not food_name or calories < 0:
                raise ValueError

            # Save food for the logged-in user
            connection.execute("""
                INSERT INTO nutrition
                (user_id, food_name, calories)
                VALUES (?, ?, ?)
            """, (session["user_id"], food_name, calories))

            connection.commit()
            connection.close()

            return redirect("/nutrition?saved=1")

        except ValueError:
            error = "Please enter valid food information."

    # Get saved food for this user
    entries = connection.execute("""
        SELECT id, food_name, calories, entry_date
        FROM nutrition
        WHERE user_id = ?
        ORDER BY id DESC
    """, (session["user_id"],)).fetchall()

    connection.close()

    # Display nutrition page
    return render_template_string(
        Path(__file__).with_name("nutrition.html").read_text(
            encoding="utf-8"
        ),
        entries=entries,
        error=error,
        saved=request.args.get("saved")
    )
# -----------------------------
# SPRINT 2 - WORKOUT TRACKING
# -----------------------------

@app.route("/workouts", methods=["GET", "POST"])
def workouts():

    # Make sure the user is logged in
    if "user_id" not in session:
        return redirect("/")

    connection = tracking_connection()
    error = None

    # Save workout when the form is submitted
    if request.method == "POST":

        workout_type = request.form.get(
            "workout_type", ""
        ).strip()

        try:
            duration = int(request.form.get("duration", ""))

            # Check if workout information is valid
            if not workout_type or duration <= 0:
                raise ValueError

            # Save workout for the logged-in user
            connection.execute("""
                INSERT INTO workouts
                (user_id, workout_type, duration)
                VALUES (?, ?, ?)
            """, (session["user_id"], workout_type, duration))

            connection.commit()
            connection.close()

            return redirect("/workouts?saved=1")

        except ValueError:
            error = "Please enter valid workout information."

    # Get saved workouts for this user
    entries = connection.execute("""
        SELECT id, workout_type, duration, entry_date
        FROM workouts
        WHERE user_id = ?
        ORDER BY id DESC
    """, (session["user_id"],)).fetchall()

    connection.close()

    # Display workout page
    return render_template_string(
        Path(__file__).with_name("workouts.html").read_text(
            encoding="utf-8"
        ),
        entries=entries,
        error=error,
        saved=request.args.get("saved")
    )
# -----------------------------
# SPRINT 2 - WATER TRACKING
# -----------------------------

@app.route("/water", methods=["GET", "POST"])
def water():

    # Make sure the user is logged in
    if "user_id" not in session:
        return redirect("/")

    connection = tracking_connection()
    error = None

    # Save water intake
    if request.method == "POST":

        try:
            amount = int(request.form.get("amount", ""))

            if amount <= 0:
                raise ValueError

            connection.execute("""
                INSERT INTO water (user_id, amount)
                VALUES (?, ?)
            """, (session["user_id"], amount))

            connection.commit()
            connection.close()

            return redirect("/water?saved=1")

        except ValueError:
            error = "Please enter a valid water amount."

    # Get saved water entries
    entries = connection.execute("""
        SELECT id, amount, entry_date
        FROM water
        WHERE user_id = ?
        ORDER BY id DESC
    """, (session["user_id"],)).fetchall()

    connection.close()

    # Display water tracking page
    return render_template_string(
        Path(__file__).with_name("water.html").read_text(
            encoding="utf-8"
        ),
        entries=entries,
        error=error,
        saved=request.args.get("saved")
    )

# -----------------------------
# SPRINT 2 - SLEEP TRACKING
# -----------------------------

@app.route("/sleep", methods=["GET", "POST"])
def sleep():

    # Make sure the user is logged in
    if "user_id" not in session:
        return redirect("/")

    connection = tracking_connection()
    error = None

    # Save sleep hours
    if request.method == "POST":

        try:
            hours = float(request.form.get("hours", ""))

            if not (0.5 <= hours <= 24):
                raise ValueError

            connection.execute("""
                INSERT INTO sleep (user_id, hours)
                VALUES (?, ?)
            """, (session["user_id"], hours))

            connection.commit()
            connection.close()

            return redirect("/sleep?saved=1")

        except ValueError:
            error = "Please enter valid sleep hours."

    # Get saved sleep entries
    entries = connection.execute("""
        SELECT id, hours, entry_date
        FROM sleep
        WHERE user_id = ?
        ORDER BY id DESC
    """, (session["user_id"],)).fetchall()

    connection.close()

    # Display sleep tracking page
    return render_template_string(
        Path(__file__).with_name("sleep.html").read_text(
            encoding="utf-8"
        ),
        entries=entries,
        error=error,
        saved=request.args.get("saved")
    )

# -----------------------------
# SPRINT 2 - MY PROGRESS PAGE
# -----------------------------

@app.route("/progress")
def progress():

    # Make sure the user is logged in
    if "user_id" not in session:
        return redirect("/")

    user_id = session["user_id"]
    today = date.today().isoformat()

    conn = tracking_connection()

    # Get today's water total
    water_total = conn.execute("""
        SELECT COALESCE(SUM(amount), 0)
        FROM water
        WHERE user_id = ? AND date(entry_date) = ?
    """, (user_id, today)).fetchone()[0]

    # Get today's workout total
    workout_total = conn.execute("""
        SELECT COALESCE(SUM(duration), 0)
        FROM workouts
        WHERE user_id = ? AND date(entry_date) = ?
    """, (user_id, today)).fetchone()[0]

    # Get today's sleep total
    sleep_total = conn.execute("""
        SELECT COALESCE(SUM(hours), 0)
        FROM sleep
        WHERE user_id = ? AND date(entry_date) = ?
    """, (user_id, today)).fetchone()[0]

    # Get today's calorie total
    calorie_total = conn.execute("""
        SELECT COALESCE(SUM(calories), 0)
        FROM nutrition
        WHERE user_id = ? AND date(entry_date) = ?
    """, (user_id, today)).fetchone()[0]

    # Get recent tracking activities
    recent_entries = conn.execute("""
        SELECT 'Water' AS category,
               CAST(amount AS TEXT) || ' mL' AS details,
               entry_date
        FROM water WHERE user_id = ?

        UNION ALL

        SELECT 'Workout',
               workout_type || ' - ' ||
               CAST(duration AS TEXT) || ' minutes',
               entry_date
        FROM workouts WHERE user_id = ?

        UNION ALL

        SELECT 'Sleep',
               CAST(hours AS TEXT) || ' hours',
               entry_date
        FROM sleep WHERE user_id = ?

        UNION ALL

        SELECT 'Nutrition',
               food_name || ' - ' ||
               CAST(calories AS TEXT) || ' calories',
               entry_date
        FROM nutrition WHERE user_id = ?

        ORDER BY entry_date DESC
        LIMIT 20
    """, (user_id, user_id, user_id, user_id)).fetchall()

    conn.close()

    # Display the progress page
    return render_template_string(
        Path(__file__).with_name("progress.html").read_text(
            encoding="utf-8"
        ),
        today=today,
        water_total=water_total,
        workout_total=workout_total,
        sleep_total=sleep_total,
        calorie_total=calorie_total,
        recent_entries=recent_entries
    )
# -----------------------------
# SPRINT 2 - DELETE TRACKING ENTRY
# -----------------------------

@app.route("/delete-entry/<category>/<int:entry_id>", methods=["POST"])
def delete_entry(category, entry_id):

    # Make sure the user is logged in
    if "user_id" not in session:
        return redirect("/")

    # Only allow our four tracking tables
    allowed_tables = ["nutrition", "workouts", "water", "sleep"]

    if category not in allowed_tables:
        return "Invalid category", 404

    # Connect to the database
    connection = tracking_connection()

    # Delete only the selected entry belonging to this user
    connection.execute(
        f"DELETE FROM {category} WHERE id = ? AND user_id = ?",
        (entry_id, session["user_id"])
    )

    connection.commit()
    connection.close()

    # Return to the correct tracking page
    return redirect("/" + category)
    
# -----------------------------
# START THE WEBSITE
# -----------------------------

if __name__ == "__main__":
    init_database()
    app.run(debug=True, use_reloader=False)
