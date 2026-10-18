# Import the Flask tools we need
from flask import Flask, request, redirect, session, send_from_directory, render_template_string
from itsdangerous import URLSafeTimedSerializer, BadSignature, SignatureExpired
from werkzeug.security import generate_password_hash, check_password_hash
# Import SQLite so we can use our database
import sqlite3

# SPRINT 2 ADDED
# Allows us to read our nutrition and workout HTML files
from pathlib import Path
from datetime import date

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
# FORGOT PASSWORD
# -----------------------------

@app.route("/forgot-password", methods=["GET", "POST"])
def forgot_password():

    if request.method == "GET":
        return send_from_directory(".", "forgot_password.html")

    email = request.form.get("email", "").strip()

    connection = tracking_connection()

    user = connection.execute(
        "SELECT id FROM users WHERE LOWER(TRIM(email)) = LOWER(TRIM(?))",
        (email,)
    ).fetchone()

    connection.close()

    if not user:
        return "If the email is registered, a reset link will be available."

    # Generate a temporary reset token
    serializer = URLSafeTimedSerializer(app.secret_key)

    token = serializer.dumps(
        user["id"],
        salt="password-reset"
    )

    # Local classroom demonstration only
    reset_link = f"http://127.0.0.1:5000/reset-password/{token}"

    return f"""
        <h2>LifeTrack Password Reset</h2>
        <p>For local testing, open this reset link:</p>
        <a href="{reset_link}">Reset My Password</a>
        <p>This link expires after 15 minutes.</p>
    """


# -----------------------------
# RESET PASSWORD
# -----------------------------

@app.route("/reset-password/<token>", methods=["GET", "POST"])
def reset_password(token):

    serializer = URLSafeTimedSerializer(app.secret_key)

    try:
        user_id = serializer.loads(
            token,
            salt="password-reset",
            max_age=900
        )

    except (BadSignature, SignatureExpired):
        return "This reset link is invalid or expired.", 400

    if request.method == "GET":
        return render_template_string(
            Path(__file__).with_name("reset_password.html").read_text(
                encoding="utf-8"
            ),
            token=token,
            error=None
        )

    password = request.form.get("password", "")
    confirm_password = request.form.get("confirm_password", "")

    if len(password) < 8 or password != confirm_password:
        return render_template_string(
            Path(__file__).with_name("reset_password.html").read_text(
                encoding="utf-8"
            ),
            token=token,
            error="Passwords must match and contain at least 8 characters."
        )

    connection = tracking_connection()

    connection.execute(
        "UPDATE users SET password = ? WHERE id = ?",
        (generate_password_hash(password), user_id)
    )

    connection.commit()
    connection.close()

    return redirect("/?reset=1")


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
    cursor.execute("""
        SELECT id, name, email, password
        FROM users
        WHERE email = ?
    """, (email,))

    # Get the account if it exists
    user = cursor.fetchone()

    # Close the database
    connection.close()


    
    # Check if the account was found
    if user and (
        check_password_hash(user[3], password)
        if user[3].startswith(("scrypt:", "pbkdf2:"))
        else user[3] == password
    ):

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



# ========== SPRINT 2 ADDED ==========

# Connect to the database for nutrition and workouts
def tracking_connection():

    connection = sqlite3.connect("health_wellness.db")

    # Allow us to access columns by their names
    connection.row_factory = sqlite3.Row

    return connection


# -----------------------------
# NUTRITION TRACKING
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
# WORKOUT TRACKING
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
# WATER TRACKING
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
        SELECT id,amount, entry_date
        FROM water
        WHERE user_id = ?
        ORDER BY id DESC
    """, (session["user_id"],)).fetchall()

    connection.close()

    return render_template_string(
        Path(__file__).with_name("water.html").read_text(
            encoding="utf-8"
        ),
        entries=entries,
        error=error,
        saved=request.args.get("saved")
    )


# -----------------------------
# SLEEP TRACKING
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
        SELECT id,hours, entry_date
        FROM sleep
        WHERE user_id = ?
        ORDER BY id DESC
    """, (session["user_id"],)).fetchall()

    connection.close()

    return render_template_string(
        Path(__file__).with_name("sleep.html").read_text(
            encoding="utf-8"
        ),
        entries=entries,
        error=error,
        saved=request.args.get("saved")
    )

# MY PROGRESS PAGE

@app.route("/progress")
def progress():

    if "user_id" not in session:
        return redirect("/")

    user_id = session["user_id"]
    today = date.today().isoformat()

    conn = tracking_connection()
    conn.row_factory = sqlite3.Row

    water_total = conn.execute(
        """
        SELECT COALESCE(SUM(amount), 0)
        FROM water
        WHERE user_id = ? AND date(entry_date) = ?
        """,
        (user_id, today)
    ).fetchone()[0]

    workout_total = conn.execute(
        """
        SELECT COALESCE(SUM(duration), 0)
        FROM workouts
        WHERE user_id = ? AND date(entry_date) = ?
        """,
        (user_id, today)
    ).fetchone()[0]

    sleep_total = conn.execute(
        """
        SELECT COALESCE(SUM(hours), 0)
        FROM sleep
        WHERE user_id = ? AND date(entry_date) = ?
        """,
        (user_id, today)
    ).fetchone()[0]

    calorie_total = conn.execute(
        """
        SELECT COALESCE(SUM(calories), 0)
        FROM nutrition
        WHERE user_id = ? AND date(entry_date) = ?
        """,
        (user_id, today)
    ).fetchone()[0]

    recent_entries = conn.execute(
        """
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
        """,
        (user_id, user_id, user_id, user_id)
    ).fetchall()

    conn.close()

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

# =====================================
# DELETE TRACKING ENTRY
# =====================================

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

if __name__ == "__main__":
    init_database()
    app.run(debug=True, use_reloader=False)
