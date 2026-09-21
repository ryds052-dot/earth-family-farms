"""Earth Family Farms Flask application and booking system."""

import re
import sqlite3
from contextlib import contextmanager
from datetime import date, datetime
from pathlib import Path

from flask import Flask, flash, redirect, render_template, request, url_for


# Create the Flask application.
# __name__ tells Flask to look for folders such as "templates" next to this file.
app = Flask(__name__)
app.config["SECRET_KEY"] = "change-this-development-key"

# Store the database beside app.py so it is easy to find while learning.
DATABASE_PATH = Path(__file__).with_name("farm.db")

# These are the accommodation options guests can select. The same list is used
# by the form and by the server, so a visitor cannot submit an unknown option.
CABINS = ("Queen Cabin", "Campsite", "Dorm Bunks", "Dorm Tent")


@contextmanager
def get_database():
    """Open a SQLite connection, then commit and close it safely."""

    connection = sqlite3.connect(DATABASE_PATH)
    connection.row_factory = sqlite3.Row
    try:
        yield connection
        connection.commit()
    finally:
        connection.close()


def initialize_database():
    """Create the bookings table if this is the first time the app runs."""

    with get_database() as connection:
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS bookings (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                guest_name TEXT NOT NULL,
                email TEXT NOT NULL,
                cabin_name TEXT NOT NULL,
                check_in TEXT NOT NULL,
                check_out TEXT NOT NULL,
                created_at TEXT NOT NULL
            )
            """
        )


initialize_database()


@app.route("/")
def home():
    """Show the Earth Family Farms landing page."""

    return render_template("index.html", cabins=CABINS)


@app.post("/book")
def book():
    """Validate and save a booking submitted by the form."""

    guest_name = request.form.get("guest_name", "").strip()
    email = request.form.get("email", "").strip().lower()
    cabin_name = request.form.get("cabin_name", "").strip()
    check_in_text = request.form.get("check_in", "").strip()
    check_out_text = request.form.get("check_out", "").strip()

    # Check basic text fields before attempting to save anything.
    if not guest_name or len(guest_name) > 100:
        flash("Please enter your name (up to 100 characters).", "error")
        return redirect(url_for("home", _anchor="book"))

    if not re.fullmatch(r"[^@\s]+@[^@\s]+\.[^@\s]+", email):
        flash("Please enter a valid email address.", "error")
        return redirect(url_for("home", _anchor="book"))

    if cabin_name not in CABINS:
        flash("Please choose one of the available cabins.", "error")
        return redirect(url_for("home", _anchor="book"))

    # HTML date inputs submit dates as YYYY-MM-DD.
    try:
        check_in = date.fromisoformat(check_in_text)
        check_out = date.fromisoformat(check_out_text)
    except ValueError:
        flash("Please choose valid check-in and check-out dates.", "error")
        return redirect(url_for("home", _anchor="book"))

    if check_in >= check_out:
        flash("Check-out must be after check-in.", "error")
        return redirect(url_for("home", _anchor="book"))

    with get_database() as connection:
        # Two date ranges overlap when the existing stay starts before the
        # requested stay ends and ends after the requested stay starts.
        overlapping_booking = connection.execute(
            """
            SELECT id
            FROM bookings
            WHERE cabin_name = ?
              AND check_in < ?
              AND check_out > ?
            LIMIT 1
            """,
            (cabin_name, check_out_text, check_in_text),
        ).fetchone()

        if overlapping_booking:
            flash(
                "That cabin is already booked for part of those dates. "
                "Please choose different dates or another cabin.",
                "error",
            )
            return redirect(url_for("home", _anchor="book"))

        connection.execute(
            """
            INSERT INTO bookings
                (guest_name, email, cabin_name, check_in, check_out, created_at)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (
                guest_name,
                email,
                cabin_name,
                check_in_text,
                check_out_text,
                datetime.now().isoformat(timespec="seconds"),
            ),
        )

    flash(
        f"Thanks, {guest_name}! Your request for {cabin_name} has been received.",
        "success",
    )
    return redirect(url_for("home", _anchor="book"))


if __name__ == "__main__":
    # This starts Flask's built-in development server.
    # debug=True automatically reloads the server when you save code changes.
    # It is useful while learning, but should be turned off for a public website.
    app.run(debug=True)
