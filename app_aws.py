from flask import (
    Flask,
    render_template,
    request,
    redirect,
    url_for,
    session,
    flash,
    jsonify,
)
import os
import boto3
import uuid
from datetime import datetime
from werkzeug.utils import secure_filename
from boto3.dynamodb.conditions import Key
from botocore.exceptions import ClientError
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
app.secret_key = "cHOgZyQn5hyqDrlIRNqxdDvecq4Sc7sD5fgrc3aB"

# AWS Configuration - Hardcoded
REGION = "us-east-1"


# Initialize AWS resources
try:
    dynamodb = boto3.resource("dynamodb", region_name=REGION)
    sns = boto3.client("sns", region_name=REGION)

    # DynamoDB Tables
    users_table = dynamodb.Table("HotelUsers")
    hotels_table = dynamodb.Table("Hotels")
    bookings_table = dynamodb.Table("HotelBookings")
    reviews_table = dynamodb.Table("HotelReviews")
    admin_table = dynamodb.Table("HotelAdmins")

    # Test connection
    dynamodb.meta.client.describe_limits()
    AWS_AVAILABLE = True
    logger.info("✓ Connected to AWS DynamoDB")
except Exception as e:
    logger.warning(f"⚠ AWS not available: {e}")
    AWS_AVAILABLE = False

# SNS Topic ARN
SNS_TOPIC_ARN = f"arn:aws:sns:us-east-1:491694398940:blissful-abodes-notifications"

# File Upload Configuration
UPLOAD_FOLDER = os.path.join(os.getcwd(), "static", "uploads")
ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "gif", "pdf"}
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
app.config["MAX_CONTENT_LENGTH"] = 16 * 1024 * 1024

# Create upload folder
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
logger.info(f"✓ Upload folder: {UPLOAD_FOLDER}")


def allowed_file(filename):
    """Check if file is allowed"""
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


def save_uploaded_file(file):
    """Save file to local storage"""
    if not file or not allowed_file(file.filename):
        return None

    try:
        filename = secure_filename(file.filename)
        unique_filename = f"{uuid.uuid4()}_{filename}"
        filepath = os.path.join(app.config["UPLOAD_FOLDER"], unique_filename)
        file.save(filepath)
        logger.info(f"✓ File saved: {filepath}")
        return unique_filename
    except Exception as e:
        logger.error(f"Error saving file: {e}")
        return None


def send_notification(subject, message):
    """Send SNS notification"""
    if not AWS_AVAILABLE:
        logger.info(f"📧 [LOCAL] {subject}: {message}")
        return

    try:
        sns.publish(TopicArn=SNS_TOPIC_ARN, Subject=subject, Message=message)
        logger.info(f"✓ SNS notification sent")
    except ClientError as e:
        logger.error(f"SNS error: {e}")


# ==================== USER ROUTES ====================


@app.route("/")
def index():
    """Home page"""
    if "username" in session:
        return redirect(url_for("home"))
    return render_template("index.html")


@app.route("/about")
def about():
    return render_template("about.html")


@app.route("/rooms")
def rooms():
    """Redirect to hotels list"""
    return redirect(url_for("hotels_list"))


@app.route("/register", methods=["GET", "POST"])
def register():
    """Alias for signup"""
    return signup()


@app.route("/dashboard")
def dashboard():
    """User dashboard - redirect to home"""
    return redirect(url_for("home"))


@app.route("/my_bookings")
def my_bookings():
    """User bookings - redirect to home"""
    return redirect(url_for("home"))


@app.route("/chatbot")
def chatbot():
    """Chatbot - not available in simplified version"""
    flash("Chat feature is not available in this version", "info")
    return redirect(url_for("index"))


@app.route("/staff_dashboard")
def staff_dashboard():
    """Staff dashboard - redirect to admin"""
    return redirect(url_for("admin_dashboard"))


@app.route("/signup", methods=["GET", "POST"])
def signup():
    """User signup"""
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        email = request.form.get("email", "").strip()
        password = request.form.get("password", "")
        phone = request.form.get("phone", "").strip()

        # Validation
        if not all([username, email, password, phone]):
            flash("All fields are required!", "danger")
            return render_template("signup.html")

        if not AWS_AVAILABLE:
            flash("AWS DynamoDB not available", "danger")
            return render_template("signup.html")

        try:
            # Check if user exists
            response = users_table.get_item(Key={"username": username})
            if "Item" in response:
                flash("Username already exists!", "danger")
                return render_template("signup.html")

            # Add user
            users_table.put_item(
                Item={
                    "username": username,
                    "email": email,
                    "password": password,
                    "phone": phone,
                    "created_at": datetime.now().isoformat(),
                }
            )

            send_notification("New User Signup", f"User {username} signed up")
            flash("Signup successful! Please login.", "success")
            return redirect(url_for("login"))
        except ClientError as e:
            logger.error(f"Signup error: {e}")
            flash(f"Error: {str(e)}", "danger")

    return render_template("signup.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    """User login"""
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")

        if not all([username, password]):
            flash("Username and password required!", "danger")
            return render_template("login.html")

        if not AWS_AVAILABLE:
            flash("AWS DynamoDB not available", "danger")
            return render_template("login.html")

        try:
            response = users_table.get_item(Key={"username": username})

            if "Item" in response and response["Item"]["password"] == password:
                session["username"] = username
                send_notification("User Login", f"User {username} logged in")
                logger.info(f"✓ User {username} logged in")
                return redirect(url_for("home"))

            flash("Invalid credentials!", "danger")
        except ClientError as e:
            logger.error(f"Login error: {e}")
            flash(f"Error: {str(e)}", "danger")

    return render_template("login.html")


@app.route("/logout")
def logout():
    """User logout"""
    username = session.get("username", "Unknown")
    session.pop("username", None)
    send_notification("User Logout", f"User {username} logged out")
    flash("Logged out successfully!", "info")
    return redirect(url_for("index"))


@app.route("/home")
def home():
    """User home page"""
    if "username" not in session:
        return redirect(url_for("login"))

    username = session["username"]

    if not AWS_AVAILABLE:
        return render_template("home.html", username=username, my_bookings=[])

    try:
        # Get user's bookings
        response = bookings_table.query(
            KeyConditionExpression=Key("username").eq(username)
        )
        my_bookings = response.get("Items", [])
        logger.info(f"✓ Retrieved {len(my_bookings)} bookings for {username}")

        return render_template("home.html", username=username, my_bookings=my_bookings)
    except ClientError as e:
        logger.error(f"Error loading home: {e}")
        return render_template("home.html", username=username, my_bookings=[])


# ==================== HOTEL ROUTES ====================


@app.route("/hotels")
def hotels_list():
    """Browse all hotels"""
    if not AWS_AVAILABLE:
        flash("AWS DynamoDB not available", "warning")
        return render_template("hotels_list.html", hotels=[])

    try:
        response = hotels_table.scan()
        hotels = response.get("Items", [])
        logger.info(f"✓ Retrieved {len(hotels)} hotels")
        return render_template("hotels_list.html", hotels=hotels)
    except ClientError as e:
        logger.error(f"Error loading hotels: {e}")
        flash(f"Error: {str(e)}", "danger")
        return render_template("hotels_list.html", hotels=[])


@app.route("/hotel/<hotel_id>")
def hotel_details(hotel_id):
    """Hotel details page"""
    if not AWS_AVAILABLE:
        flash("AWS DynamoDB not available", "warning")
        return redirect(url_for("hotels_list"))

    try:
        response = hotels_table.get_item(Key={"id": hotel_id})
        hotel = response.get("Item")

        if not hotel:
            flash("Hotel not found!", "danger")
            return redirect(url_for("hotels_list"))

        # Get reviews
        try:
            reviews_response = reviews_table.query(
                KeyConditionExpression=Key("hotel_id").eq(hotel_id)
            )
            reviews = reviews_response.get("Items", [])
        except:
            reviews = []

        logger.info(f"✓ Retrieved hotel {hotel_id}")
        return render_template("hotel_details.html", hotel=hotel, reviews=reviews)
    except ClientError as e:
        logger.error(f"Error loading hotel: {e}")
        flash(f"Error: {str(e)}", "danger")
        return redirect(url_for("hotels_list"))


@app.route("/book/<hotel_id>", methods=["GET", "POST"])
def book_hotel(hotel_id):
    """Book a hotel"""
    if "username" not in session:
        flash("Please login first", "warning")
        return redirect(url_for("login"))

    if not AWS_AVAILABLE:
        flash("AWS DynamoDB not available", "warning")
        return redirect(url_for("hotel_details", hotel_id=hotel_id))

    try:
        response = hotels_table.get_item(Key={"id": hotel_id})
        hotel = response.get("Item")

        if not hotel:
            flash("Hotel not found!", "danger")
            return redirect(url_for("hotels_list"))

        if request.method == "POST":
            check_in = request.form.get("check_in")
            check_out = request.form.get("check_out")
            rooms = int(request.form.get("rooms", 1))

            if not all([check_in, check_out, rooms]):
                flash("All details required!", "danger")
                return render_template("booking.html", hotel=hotel)

            # Create booking
            booking_id = str(uuid.uuid4())
            booking_item = {
                "booking_id": booking_id,
                "username": session["username"],
                "hotel_id": hotel_id,
                "hotel_name": hotel.get("name"),
                "check_in": check_in,
                "check_out": check_out,
                "rooms": rooms,
                "total_price": float(hotel.get("price_per_night", 0)) * rooms,
                "status": "confirmed",
                "booking_date": datetime.now().isoformat(),
            }

            bookings_table.put_item(Item=booking_item)
            send_notification("Booking Confirmed", f"Booking {booking_id} confirmed")
            logger.info(f"✓ Booking {booking_id} created")

            flash("Booking confirmed!", "success")
            return redirect(url_for("home"))

        return render_template("booking.html", hotel=hotel)
    except ClientError as e:
        logger.error(f"Booking error: {e}")
        flash(f"Error: {str(e)}", "danger")
        return redirect(url_for("hotel_details", hotel_id=hotel_id))


@app.route("/review/<hotel_id>", methods=["POST"])
def submit_review(hotel_id):
    """Submit review"""
    if "username" not in session:
        flash("Please login first", "warning")
        return redirect(url_for("login"))

    if not AWS_AVAILABLE:
        flash("AWS DynamoDB not available", "warning")
        return redirect(url_for("hotel_details", hotel_id=hotel_id))

    try:
        rating = request.form.get("rating")
        comment = request.form.get("comment")

        if not all([rating, comment]):
            flash("Rating and comment required!", "danger")
            return redirect(url_for("hotel_details", hotel_id=hotel_id))

        review_id = str(uuid.uuid4())
        reviews_table.put_item(
            Item={
                "hotel_id": hotel_id,
                "review_id": review_id,
                "username": session["username"],
                "rating": int(rating),
                "comment": comment,
                "created_at": datetime.now().isoformat(),
            }
        )

        send_notification("New Review", f"Review submitted for hotel {hotel_id}")
        logger.info(f"✓ Review {review_id} created")
        flash("Review submitted!", "success")
    except ClientError as e:
        logger.error(f"Review error: {e}")
        flash(f"Error: {str(e)}", "danger")

    return redirect(url_for("hotel_details", hotel_id=hotel_id))


# ==================== ADMIN ROUTES ====================


@app.route("/admin/signup", methods=["GET", "POST"])
def admin_signup():
    """Admin signup"""
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")

        if not all([username, password]):
            flash("All fields required!", "danger")
            return render_template("admin_signup.html")

        if not AWS_AVAILABLE:
            flash("AWS DynamoDB not available", "danger")
            return render_template("admin_signup.html")

        try:
            response = admin_table.get_item(Key={"username": username})
            if "Item" in response:
                flash("Admin already exists!", "danger")
                return render_template("admin_signup.html")

            admin_table.put_item(
                Item={
                    "username": username,
                    "password": password,
                    "created_at": datetime.now().isoformat(),
                }
            )

            send_notification("Admin Signup", f"Admin {username} registered")
            flash("Admin signup successful! Please login.", "success")
            return redirect(url_for("admin_login"))
        except ClientError as e:
            logger.error(f"Admin signup error: {e}")
            flash(f"Error: {str(e)}", "danger")

    return render_template("admin_signup.html")


@app.route("/admin/login", methods=["GET", "POST"])
def admin_login():
    """Admin login"""
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")

        if not all([username, password]):
            flash("Username and password required!", "danger")
            return render_template("admin_login.html")

        if not AWS_AVAILABLE:
            flash("AWS DynamoDB not available", "danger")
            return render_template("admin_login.html")

        try:
            response = admin_table.get_item(Key={"username": username})

            if "Item" in response and response["Item"]["password"] == password:
                session["admin"] = username
                logger.info(f"✓ Admin {username} logged in")
                return redirect(url_for("admin_dashboard"))

            flash("Invalid credentials!", "danger")
        except ClientError as e:
            logger.error(f"Admin login error: {e}")
            flash(f"Error: {str(e)}", "danger")

    return render_template("admin_login.html")


@app.route("/admin/dashboard")
def admin_dashboard():
    """Admin dashboard"""
    if "admin" not in session:
        return redirect(url_for("admin_login"))

    if not AWS_AVAILABLE:
        return render_template(
            "admin_dashboard.html",
            username=session["admin"],
            users=[],
            hotels=[],
            bookings=[],
        )

    try:
        users = users_table.scan().get("Items", [])
        hotels = hotels_table.scan().get("Items", [])
        bookings = bookings_table.scan().get("Items", [])

        logger.info(
            f"✓ Admin dashboard: {len(users)} users, {len(hotels)} hotels, {len(bookings)} bookings"
        )

        return render_template(
            "admin_dashboard.html",
            username=session["admin"],
            users=users,
            hotels=hotels,
            bookings=bookings,
            total_users=len(users),
            total_hotels=len(hotels),
            total_bookings=len(bookings),
        )
    except ClientError as e:
        logger.error(f"Dashboard error: {e}")
        return render_template(
            "admin_dashboard.html",
            username=session["admin"],
            users=[],
            hotels=[],
            bookings=[],
        )


@app.route("/admin/create-hotel", methods=["GET", "POST"])
def admin_create_hotel():
    """Create hotel"""
    if "admin" not in session:
        return redirect(url_for("admin_login"))

    if not AWS_AVAILABLE:
        flash("AWS DynamoDB not available", "danger")
        return render_template("admin_create_hotel.html", username=session["admin"])

    if request.method == "POST":
        try:
            name = request.form.get("name", "").strip()
            location = request.form.get("location", "").strip()
            description = request.form.get("description", "").strip()
            price_per_night = float(request.form.get("price_per_night", 0))
            rooms_available = int(request.form.get("rooms_available", 0))

            if not all([name, location, description, price_per_night, rooms_available]):
                flash("All fields required!", "danger")
                return render_template(
                    "admin_create_hotel.html", username=session["admin"]
                )

            # Handle image upload
            image_filename = None
            if "image" in request.files:
                image = request.files["image"]
                if image and allowed_file(image.filename):
                    image_filename = save_uploaded_file(image)

            hotel_id = str(uuid.uuid4())
            hotels_table.put_item(
                Item={
                    "id": hotel_id,
                    "name": name,
                    "location": location,
                    "description": description,
                    "price_per_night": price_per_night,
                    "rooms_available": rooms_available,
                    "image": image_filename,
                    "created_by": session["admin"],
                    "created_at": datetime.now().isoformat(),
                }
            )

            send_notification("New Hotel", f"Hotel '{name}' created")
            logger.info(f"✓ Hotel {hotel_id} created")
            flash("Hotel created successfully!", "success")
            return redirect(url_for("admin_dashboard"))
        except ClientError as e:
            logger.error(f"Create hotel error: {e}")
            flash(f"Error: {str(e)}", "danger")

    return render_template("admin_create_hotel.html", username=session["admin"])


@app.route("/admin/edit-hotel/<hotel_id>", methods=["GET", "POST"])
def admin_edit_hotel(hotel_id):
    """Edit hotel"""
    if "admin" not in session:
        return redirect(url_for("admin_login"))

    if not AWS_AVAILABLE:
        flash("AWS DynamoDB not available", "danger")
        return redirect(url_for("admin_dashboard"))

    try:
        response = hotels_table.get_item(Key={"id": hotel_id})
        hotel = response.get("Item")

        if not hotel:
            flash("Hotel not found!", "danger")
            return redirect(url_for("admin_dashboard"))

        if request.method == "POST":
            hotel["name"] = request.form.get("name", "").strip()
            hotel["location"] = request.form.get("location", "").strip()
            hotel["description"] = request.form.get("description", "").strip()
            hotel["price_per_night"] = float(request.form.get("price_per_night", 0))
            hotel["rooms_available"] = int(request.form.get("rooms_available", 0))
            hotel["updated_at"] = datetime.now().isoformat()

            # Handle image update
            if "image" in request.files:
                image = request.files["image"]
                if image and allowed_file(image.filename):
                    image_filename = save_uploaded_file(image)
                    hotel["image"] = image_filename

            hotels_table.put_item(Item=hotel)
            send_notification("Hotel Updated", f"Hotel '{hotel['name']}' updated")
            logger.info(f"✓ Hotel {hotel_id} updated")
            flash("Hotel updated successfully!", "success")
            return redirect(url_for("admin_dashboard"))

        return render_template(
            "admin_edit_hotel.html", hotel=hotel, username=session["admin"]
        )
    except ClientError as e:
        logger.error(f"Edit hotel error: {e}")
        flash(f"Error: {str(e)}", "danger")
        return redirect(url_for("admin_dashboard"))


@app.route("/admin/delete-hotel/<hotel_id>", methods=["POST"])
def admin_delete_hotel(hotel_id):
    """Delete hotel"""
    if "admin" not in session:
        return redirect(url_for("admin_login"))

    if not AWS_AVAILABLE:
        flash("AWS DynamoDB not available", "danger")
        return redirect(url_for("admin_dashboard"))

    try:
        response = hotels_table.get_item(Key={"id": hotel_id})
        hotel = response.get("Item")

        hotels_table.delete_item(Key={"id": hotel_id})
        send_notification("Hotel Deleted", f"Hotel '{hotel.get('name')}' deleted")
        logger.info(f"✓ Hotel {hotel_id} deleted")
        flash("Hotel deleted successfully!", "success")
    except ClientError as e:
        logger.error(f"Delete hotel error: {e}")
        flash(f"Error: {str(e)}", "danger")

    return redirect(url_for("admin_dashboard"))


@app.route("/admin/logout")
def admin_logout():
    """Admin logout"""
    session.pop("admin", None)
    logger.info("✓ Admin logged out")
    return redirect(url_for("index"))


@app.route("/health")
def health_check():
    """Health check endpoint"""
    return (
        jsonify(
            {
                "status": "healthy",
                "aws_available": AWS_AVAILABLE,
                "region": REGION,
                "timestamp": datetime.now().isoformat(),
            }
        ),
        200,
    )


@app.errorhandler(404)
def page_not_found(e):
    return render_template("404.html"), 404


@app.errorhandler(500)
def internal_server_error(e):
    logger.error(f"Server error: {e}")
    return render_template("500.html"), 500


if __name__ == "__main__":
    logger.info("=" * 60)
    logger.info("Blissful Abodes - AWS Hotel Booking System")
    logger.info("=" * 60)
    logger.info(f"Region: {REGION}")
    logger.info(f"AWS Available: {AWS_AVAILABLE}")
    logger.info(f"Upload Folder: {UPLOAD_FOLDER}")
    logger.info("=" * 60)

    app.run(host="0.0.0.0", port=5000, debug=False)
