import os
import sqlite3
from datetime import date, datetime
from functools import wraps

from flask import (
    Flask,
    flash,
    g,
    redirect,
    render_template,
    request,
    session,
    url_for,
)
from werkzeug.security import check_password_hash, generate_password_hash


BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "rental_app.db")
DEFAULT_IMAGE = "https://images.unsplash.com/photo-1494526585095-c41746248156?auto=format&fit=crop&w=1200&q=80"

app = Flask(__name__, template_folder="templates", static_folder="static")
app.config["SECRET_KEY"] = os.getenv("RENTAL_SECRET_KEY", "change-me-in-production")
app.config["DATABASE"] = DB_PATH


def get_db():
    if "db" not in g:
        g.db = sqlite3.connect(app.config["DATABASE"])
        g.db.row_factory = sqlite3.Row
        g.db.execute("PRAGMA foreign_keys = ON;")
    return g.db


@app.teardown_appcontext
def close_db(_error):
    db = g.pop("db", None)
    if db is not None:
        db.close()


def add_column_if_missing(db, table, column, definition):
    existing = {row["name"] for row in db.execute(f"PRAGMA table_info({table})").fetchall()}
    if column not in existing:
        db.execute(f"ALTER TABLE {table} ADD COLUMN {column} {definition}")


def init_db():
    db = get_db()
    db.executescript(
        """
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            created_at TEXT NOT NULL
        );

        CREATE TABLE IF NOT EXISTS listings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            owner_id INTEGER NOT NULL,
            title TEXT NOT NULL,
            city TEXT NOT NULL,
            address TEXT NOT NULL,
            space_type TEXT NOT NULL,
            price_per_day REAL NOT NULL,
            description TEXT NOT NULL,
            available INTEGER NOT NULL DEFAULT 1,
            created_at TEXT NOT NULL,
            country TEXT NOT NULL DEFAULT 'India',
            state TEXT NOT NULL DEFAULT '',
            latitude REAL,
            longitude REAL,
            image_url TEXT,
            virtual_tour_url TEXT,
            amenities TEXT NOT NULL DEFAULT '',
            max_guests INTEGER NOT NULL DEFAULT 1,
            min_stay_days INTEGER NOT NULL DEFAULT 1,
            cleaning_fee REAL NOT NULL DEFAULT 0
        );

        CREATE TABLE IF NOT EXISTS bookings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            listing_id INTEGER NOT NULL,
            renter_id INTEGER NOT NULL,
            start_date TEXT NOT NULL,
            end_date TEXT NOT NULL,
            message TEXT,
            status TEXT NOT NULL DEFAULT 'pending',
            created_at TEXT NOT NULL,
            total_price REAL NOT NULL DEFAULT 0,
            FOREIGN KEY(listing_id) REFERENCES listings(id) ON DELETE CASCADE,
            FOREIGN KEY(renter_id) REFERENCES users(id)
        );

        CREATE TABLE IF NOT EXISTS reviews (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            listing_id INTEGER NOT NULL,
            renter_id INTEGER NOT NULL,
            rating INTEGER NOT NULL,
            comment TEXT NOT NULL DEFAULT '',
            created_at TEXT NOT NULL,
            UNIQUE(listing_id, renter_id),
            FOREIGN KEY(listing_id) REFERENCES listings(id) ON DELETE CASCADE,
            FOREIGN KEY(renter_id) REFERENCES users(id)
        );
        """
    )

    add_column_if_missing(db, "listings", "country", "TEXT NOT NULL DEFAULT 'India'")
    add_column_if_missing(db, "listings", "state", "TEXT NOT NULL DEFAULT ''")
    add_column_if_missing(db, "listings", "latitude", "REAL")
    add_column_if_missing(db, "listings", "longitude", "REAL")
    add_column_if_missing(db, "listings", "image_url", "TEXT")
    add_column_if_missing(db, "listings", "virtual_tour_url", "TEXT")
    add_column_if_missing(db, "listings", "amenities", "TEXT NOT NULL DEFAULT ''")
    add_column_if_missing(db, "listings", "max_guests", "INTEGER NOT NULL DEFAULT 1")
    add_column_if_missing(db, "listings", "min_stay_days", "INTEGER NOT NULL DEFAULT 1")
    add_column_if_missing(db, "listings", "cleaning_fee", "REAL NOT NULL DEFAULT 0")
    add_column_if_missing(db, "bookings", "total_price", "REAL NOT NULL DEFAULT 0")

    db.commit()


def login_required(view):
    @wraps(view)
    def wrapped(*args, **kwargs):
        if g.user is None:
            flash("Please log in to continue.", "error")
            return redirect(url_for("login"))
        return view(*args, **kwargs)

    return wrapped


def parse_date(date_text):
    try:
        return datetime.strptime(date_text, "%Y-%m-%d").date()
    except ValueError:
        return None


def nights_between(start_dt, end_dt):
    return (end_dt - start_dt).days + 1


def parse_amenities(raw):
    return [item.strip() for item in (raw or "").split(",") if item.strip()]


@app.before_request
def load_logged_in_user():
    user_id = session.get("user_id")
    if user_id is None:
        g.user = None
        return

    db = get_db()
    g.user = db.execute("SELECT * FROM users WHERE id = ?", (user_id,)).fetchone()


@app.route("/")
def home():
    db = get_db()
    city = request.args.get("city", "").strip()
    space_type = request.args.get("space_type", "").strip()
    min_price = request.args.get("min_price", "").strip()
    max_price = request.args.get("max_price", "").strip()
    guests = request.args.get("guests", "").strip()
    start_date = request.args.get("start_date", "").strip()
    end_date = request.args.get("end_date", "").strip()

    query = """
        SELECT
            l.*,
            u.username AS owner_name,
            COALESCE(ROUND(AVG(r.rating), 1), 0) AS avg_rating,
            COUNT(r.id) AS review_count
        FROM listings l
        JOIN users u ON l.owner_id = u.id
        LEFT JOIN reviews r ON r.listing_id = l.id
        WHERE l.available = 1
    """
    params = []

    if city:
        query += " AND l.city LIKE ?"
        params.append(f"%{city}%")
    if space_type:
        query += " AND l.space_type = ?"
        params.append(space_type)
    if guests:
        try:
            guests_value = int(guests)
            if guests_value > 0:
                query += " AND l.max_guests >= ?"
                params.append(guests_value)
        except ValueError:
            flash("Guests filter must be a number.", "error")
    if min_price:
        try:
            min_price_value = float(min_price)
            query += " AND l.price_per_day >= ?"
            params.append(min_price_value)
        except ValueError:
            flash("Min price must be a number.", "error")
    if max_price:
        try:
            max_price_value = float(max_price)
            query += " AND l.price_per_day <= ?"
            params.append(max_price_value)
        except ValueError:
            flash("Max price must be a number.", "error")

    start_dt = parse_date(start_date) if start_date else None
    end_dt = parse_date(end_date) if end_date else None
    if start_date or end_date:
        if not start_dt or not end_dt or end_dt < start_dt:
            flash("Enter a valid availability date range.", "error")
        else:
            query += """
                AND NOT EXISTS (
                    SELECT 1
                    FROM bookings b
                    WHERE b.listing_id = l.id
                      AND b.status IN ('pending', 'approved')
                      AND NOT (date(b.end_date) < date(?) OR date(b.start_date) > date(?))
                )
            """
            params.extend([start_date, end_date])

    query += " GROUP BY l.id ORDER BY l.created_at DESC"
    listings = db.execute(query, params).fetchall()
    return render_template("rental/home.html", listings=listings, parse_amenities=parse_amenities)


@app.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")

        if not username or not email or not password:
            flash("All fields are required.", "error")
            return render_template("rental/signup.html")
        if len(password) < 6:
            flash("Password must be at least 6 characters.", "error")
            return render_template("rental/signup.html")

        db = get_db()
        try:
            db.execute(
                """
                INSERT INTO users (username, email, password_hash, created_at)
                VALUES (?, ?, ?, ?)
                """,
                (username, email, generate_password_hash(password), datetime.utcnow().isoformat()),
            )
            db.commit()
            flash("Account created. Please log in.", "success")
            return redirect(url_for("login"))
        except sqlite3.IntegrityError:
            flash("Username or email already exists.", "error")

    return render_template("rental/signup.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")
        db = get_db()
        user = db.execute("SELECT * FROM users WHERE email = ?", (email,)).fetchone()

        if user is None or not check_password_hash(user["password_hash"], password):
            flash("Invalid email or password.", "error")
            return render_template("rental/login.html")

        session.clear()
        session["user_id"] = user["id"]
        flash("Welcome back.", "success")
        return redirect(url_for("home"))

    return render_template("rental/login.html")


@app.route("/logout")
def logout():
    session.clear()
    flash("Logged out successfully.", "success")
    return redirect(url_for("home"))


@app.route("/listing/new", methods=["GET", "POST"])
@login_required
def new_listing():
    if request.method == "POST":
        return save_listing()
    return render_template("rental/listing_form.html", listing=None)


def _validate_listing_form(form):
    title = form.get("title", "").strip()
    city = form.get("city", "").strip()
    state = form.get("state", "").strip()
    country = form.get("country", "").strip() or "India"
    address = form.get("address", "").strip()
    space_type = form.get("space_type", "").strip()
    description = form.get("description", "").strip()
    amenities = form.get("amenities", "").strip()
    image_url = form.get("image_url", "").strip()
    virtual_tour_url = form.get("virtual_tour_url", "").strip()
    available = 1 if form.get("available") == "on" else 0

    if not all([title, city, address, space_type, description]):
        raise ValueError("Title, city, address, type and description are required.")

    try:
        price_per_day = float(form.get("price_per_day", "0").strip())
        if price_per_day <= 0:
            raise ValueError
    except ValueError:
        raise ValueError("Price per day must be a positive number.")

    try:
        max_guests = int(form.get("max_guests", "1").strip())
        if max_guests <= 0:
            raise ValueError
    except ValueError:
        raise ValueError("Max guests must be a positive whole number.")

    try:
        min_stay_days = int(form.get("min_stay_days", "1").strip())
        if min_stay_days <= 0:
            raise ValueError
    except ValueError:
        raise ValueError("Minimum stay must be a positive whole number.")

    try:
        cleaning_fee = float(form.get("cleaning_fee", "0").strip() or "0")
        if cleaning_fee < 0:
            raise ValueError
    except ValueError:
        raise ValueError("Cleaning fee must be zero or more.")

    latitude_raw = form.get("latitude", "").strip()
    longitude_raw = form.get("longitude", "").strip()
    latitude = None
    longitude = None
    if latitude_raw:
        try:
            latitude = float(latitude_raw)
            if latitude < -90 or latitude > 90:
                raise ValueError
        except ValueError:
            raise ValueError("Latitude must be between -90 and 90.")
    if longitude_raw:
        try:
            longitude = float(longitude_raw)
            if longitude < -180 or longitude > 180:
                raise ValueError
        except ValueError:
            raise ValueError("Longitude must be between -180 and 180.")

    return {
        "title": title,
        "city": city,
        "state": state,
        "country": country,
        "address": address,
        "space_type": space_type,
        "price_per_day": price_per_day,
        "description": description,
        "available": available,
        "amenities": amenities,
        "image_url": image_url,
        "virtual_tour_url": virtual_tour_url,
        "max_guests": max_guests,
        "min_stay_days": min_stay_days,
        "cleaning_fee": cleaning_fee,
        "latitude": latitude,
        "longitude": longitude,
    }


def save_listing(listing_id=None):
    db = get_db()
    try:
        data = _validate_listing_form(request.form)
    except ValueError as exc:
        flash(str(exc), "error")
        listing = request.form.to_dict()
        listing["available"] = request.form.get("available") == "on"
        return render_template("rental/listing_form.html", listing=listing)

    if not data["image_url"]:
        data["image_url"] = DEFAULT_IMAGE

    if listing_id is None:
        db.execute(
            """
            INSERT INTO listings (
                owner_id, title, city, state, country, address, space_type,
                price_per_day, description, available, created_at,
                amenities, image_url, virtual_tour_url,
                max_guests, min_stay_days, cleaning_fee, latitude, longitude
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                g.user["id"],
                data["title"],
                data["city"],
                data["state"],
                data["country"],
                data["address"],
                data["space_type"],
                data["price_per_day"],
                data["description"],
                data["available"],
                datetime.utcnow().isoformat(),
                data["amenities"],
                data["image_url"],
                data["virtual_tour_url"],
                data["max_guests"],
                data["min_stay_days"],
                data["cleaning_fee"],
                data["latitude"],
                data["longitude"],
            ),
        )
        db.commit()
        flash("Listing created.", "success")
        return redirect(url_for("dashboard"))

    listing = db.execute("SELECT * FROM listings WHERE id = ?", (listing_id,)).fetchone()
    if listing is None or listing["owner_id"] != g.user["id"]:
        flash("Listing not found or access denied.", "error")
        return redirect(url_for("home"))

    db.execute(
        """
        UPDATE listings
        SET title = ?, city = ?, state = ?, country = ?, address = ?, space_type = ?,
            price_per_day = ?, description = ?, available = ?, amenities = ?,
            image_url = ?, virtual_tour_url = ?, max_guests = ?, min_stay_days = ?,
            cleaning_fee = ?, latitude = ?, longitude = ?
        WHERE id = ?
        """,
        (
            data["title"],
            data["city"],
            data["state"],
            data["country"],
            data["address"],
            data["space_type"],
            data["price_per_day"],
            data["description"],
            data["available"],
            data["amenities"],
            data["image_url"],
            data["virtual_tour_url"],
            data["max_guests"],
            data["min_stay_days"],
            data["cleaning_fee"],
            data["latitude"],
            data["longitude"],
            listing_id,
        ),
    )
    db.commit()
    flash("Listing updated.", "success")
    return redirect(url_for("listing_detail", listing_id=listing_id))


@app.route("/listing/<int:listing_id>")
def listing_detail(listing_id):
    db = get_db()
    listing = db.execute(
        """
        SELECT
            l.*,
            u.username AS owner_name,
            COALESCE(ROUND(AVG(r.rating), 1), 0) AS avg_rating,
            COUNT(r.id) AS review_count
        FROM listings l
        JOIN users u ON l.owner_id = u.id
        LEFT JOIN reviews r ON r.listing_id = l.id
        WHERE l.id = ?
        GROUP BY l.id
        """,
        (listing_id,),
    ).fetchone()
    if listing is None:
        flash("Listing not found.", "error")
        return redirect(url_for("home"))

    bookings = []
    if g.user and g.user["id"] == listing["owner_id"]:
        bookings = db.execute(
            """
            SELECT b.*, u.username AS renter_name
            FROM bookings b
            JOIN users u ON b.renter_id = u.id
            WHERE b.listing_id = ?
            ORDER BY b.created_at DESC
            """,
            (listing_id,),
        ).fetchall()

    reviews = db.execute(
        """
        SELECT r.*, u.username AS renter_name
        FROM reviews r
        JOIN users u ON r.renter_id = u.id
        WHERE r.listing_id = ?
        ORDER BY r.created_at DESC
        """,
        (listing_id,),
    ).fetchall()

    can_review = False
    if g.user and g.user["id"] != listing["owner_id"]:
        eligible = db.execute(
            """
            SELECT 1
            FROM bookings
            WHERE listing_id = ?
              AND renter_id = ?
              AND status = 'approved'
              AND date(end_date) < date('now')
            LIMIT 1
            """,
            (listing_id, g.user["id"]),
        ).fetchone()
        can_review = eligible is not None

    return render_template(
        "rental/listing_detail.html",
        listing=listing,
        bookings=bookings,
        reviews=reviews,
        can_review=can_review,
        parse_amenities=parse_amenities,
    )


@app.route("/listing/<int:listing_id>/edit", methods=["GET", "POST"])
@login_required
def edit_listing(listing_id):
    db = get_db()
    listing = db.execute("SELECT * FROM listings WHERE id = ?", (listing_id,)).fetchone()
    if listing is None or listing["owner_id"] != g.user["id"]:
        flash("Listing not found or access denied.", "error")
        return redirect(url_for("home"))

    if request.method == "POST":
        return save_listing(listing_id=listing_id)

    return render_template("rental/listing_form.html", listing=listing)


@app.route("/listing/<int:listing_id>/delete", methods=["POST"])
@login_required
def delete_listing(listing_id):
    db = get_db()
    listing = db.execute("SELECT * FROM listings WHERE id = ?", (listing_id,)).fetchone()
    if listing is None or listing["owner_id"] != g.user["id"]:
        flash("Listing not found or access denied.", "error")
        return redirect(url_for("home"))

    db.execute("DELETE FROM listings WHERE id = ?", (listing_id,))
    db.commit()
    flash("Listing deleted.", "success")
    return redirect(url_for("dashboard"))


@app.route("/listing/<int:listing_id>/book", methods=["POST"])
@login_required
def create_booking(listing_id):
    db = get_db()
    listing = db.execute("SELECT * FROM listings WHERE id = ?", (listing_id,)).fetchone()
    if listing is None:
        flash("Listing not found.", "error")
        return redirect(url_for("home"))
    if listing["owner_id"] == g.user["id"]:
        flash("You cannot book your own listing.", "error")
        return redirect(url_for("listing_detail", listing_id=listing_id))
    if listing["available"] != 1:
        flash("This listing is currently unavailable.", "error")
        return redirect(url_for("listing_detail", listing_id=listing_id))

    start_date = request.form.get("start_date", "").strip()
    end_date = request.form.get("end_date", "").strip()
    message = request.form.get("message", "").strip()

    start_dt = parse_date(start_date)
    end_dt = parse_date(end_date)
    if not start_dt or not end_dt or end_dt < start_dt:
        flash("Enter valid booking dates.", "error")
        return redirect(url_for("listing_detail", listing_id=listing_id))
    if start_dt < date.today():
        flash("Booking start date cannot be in the past.", "error")
        return redirect(url_for("listing_detail", listing_id=listing_id))

    nights = nights_between(start_dt, end_dt)
    if nights < listing["min_stay_days"]:
        flash(f"Minimum stay for this space is {listing['min_stay_days']} day(s).", "error")
        return redirect(url_for("listing_detail", listing_id=listing_id))

    overlap = db.execute(
        """
        SELECT 1
        FROM bookings
        WHERE listing_id = ?
          AND status IN ('pending', 'approved')
          AND NOT (date(end_date) < date(?) OR date(start_date) > date(?))
        LIMIT 1
        """,
        (listing_id, start_date, end_date),
    ).fetchone()
    if overlap:
        flash("This date range is already requested/booked.", "error")
        return redirect(url_for("listing_detail", listing_id=listing_id))

    total_price = (nights * listing["price_per_day"]) + listing["cleaning_fee"]
    db.execute(
        """
        INSERT INTO bookings (
            listing_id, renter_id, start_date, end_date, message, status, created_at, total_price
        )
        VALUES (?, ?, ?, ?, ?, 'pending', ?, ?)
        """,
        (
            listing_id,
            g.user["id"],
            start_date,
            end_date,
            message,
            datetime.utcnow().isoformat(),
            total_price,
        ),
    )
    db.commit()
    flash("Booking request sent.", "success")
    return redirect(url_for("dashboard"))


@app.route("/booking/<int:booking_id>/status", methods=["POST"])
@login_required
def update_booking_status(booking_id):
    status = request.form.get("status", "").strip().lower()
    if status not in {"approved", "rejected", "cancelled"}:
        flash("Invalid status update.", "error")
        return redirect(url_for("dashboard"))

    db = get_db()
    booking = db.execute(
        """
        SELECT b.*, l.owner_id
        FROM bookings b
        JOIN listings l ON b.listing_id = l.id
        WHERE b.id = ?
        """,
        (booking_id,),
    ).fetchone()

    if booking is None:
        flash("Booking not found.", "error")
        return redirect(url_for("dashboard"))

    if status in {"approved", "rejected"} and booking["owner_id"] != g.user["id"]:
        flash("Only the listing owner can approve or reject requests.", "error")
        return redirect(url_for("dashboard"))
    if status == "cancelled" and booking["renter_id"] != g.user["id"]:
        flash("Only the renter can cancel this booking.", "error")
        return redirect(url_for("dashboard"))

    if status == "approved":
        overlap = db.execute(
            """
            SELECT 1
            FROM bookings
            WHERE listing_id = ?
              AND id != ?
              AND status = 'approved'
              AND NOT (date(end_date) < date(?) OR date(start_date) > date(?))
            LIMIT 1
            """,
            (booking["listing_id"], booking_id, booking["start_date"], booking["end_date"]),
        ).fetchone()
        if overlap:
            flash("Cannot approve. Another approved booking overlaps these dates.", "error")
            return redirect(url_for("listing_detail", listing_id=booking["listing_id"]))

    db.execute("UPDATE bookings SET status = ? WHERE id = ?", (status, booking_id))
    db.commit()
    flash("Booking status updated.", "success")
    return redirect(url_for("listing_detail", listing_id=booking["listing_id"]))


@app.route("/listing/<int:listing_id>/review", methods=["POST"])
@login_required
def add_review(listing_id):
    db = get_db()
    listing = db.execute("SELECT * FROM listings WHERE id = ?", (listing_id,)).fetchone()
    if listing is None:
        flash("Listing not found.", "error")
        return redirect(url_for("home"))
    if listing["owner_id"] == g.user["id"]:
        flash("Owners cannot review their own listings.", "error")
        return redirect(url_for("listing_detail", listing_id=listing_id))

    eligible = db.execute(
        """
        SELECT 1
        FROM bookings
        WHERE listing_id = ?
          AND renter_id = ?
          AND status = 'approved'
          AND date(end_date) < date('now')
        LIMIT 1
        """,
        (listing_id, g.user["id"]),
    ).fetchone()
    if not eligible:
        flash("You can review only after a completed approved stay.", "error")
        return redirect(url_for("listing_detail", listing_id=listing_id))

    rating_raw = request.form.get("rating", "").strip()
    comment = request.form.get("comment", "").strip()
    try:
        rating = int(rating_raw)
        if rating < 1 or rating > 5:
            raise ValueError
    except ValueError:
        flash("Rating must be between 1 and 5.", "error")
        return redirect(url_for("listing_detail", listing_id=listing_id))

    db.execute(
        """
        INSERT INTO reviews (listing_id, renter_id, rating, comment, created_at)
        VALUES (?, ?, ?, ?, ?)
        ON CONFLICT(listing_id, renter_id) DO UPDATE SET
            rating = excluded.rating,
            comment = excluded.comment,
            created_at = excluded.created_at
        """,
        (listing_id, g.user["id"], rating, comment, datetime.utcnow().isoformat()),
    )
    db.commit()
    flash("Review saved.", "success")
    return redirect(url_for("listing_detail", listing_id=listing_id))


@app.route("/dashboard")
@login_required
def dashboard():
    db = get_db()
    my_listings = db.execute(
        """
        SELECT
            l.*,
            COUNT(b.id) AS total_requests,
            SUM(CASE WHEN b.status = 'approved' THEN 1 ELSE 0 END) AS approved_requests
        FROM listings l
        LEFT JOIN bookings b ON b.listing_id = l.id
        WHERE l.owner_id = ?
        GROUP BY l.id
        ORDER BY l.created_at DESC
        """,
        (g.user["id"],),
    ).fetchall()

    incoming_bookings = db.execute(
        """
        SELECT b.*, l.title AS listing_title, u.username AS renter_name
        FROM bookings b
        JOIN listings l ON b.listing_id = l.id
        JOIN users u ON b.renter_id = u.id
        WHERE l.owner_id = ?
        ORDER BY b.created_at DESC
        """,
        (g.user["id"],),
    ).fetchall()

    my_bookings = db.execute(
        """
        SELECT b.*, l.title AS listing_title, l.city, u.username AS owner_name
        FROM bookings b
        JOIN listings l ON b.listing_id = l.id
        JOIN users u ON l.owner_id = u.id
        WHERE b.renter_id = ?
        ORDER BY b.created_at DESC
        """,
        (g.user["id"],),
    ).fetchall()

    return render_template(
        "rental/dashboard.html",
        my_listings=my_listings,
        incoming_bookings=incoming_bookings,
        my_bookings=my_bookings,
    )


if __name__ == "__main__":
    with app.app_context():
        init_db()
    app.run(debug=True, port=5050)
