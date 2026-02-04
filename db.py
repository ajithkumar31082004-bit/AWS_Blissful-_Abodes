import boto3
from boto3.dynamodb.conditions import Key, Attr
from botocore.exceptions import ClientError
from decimal import Decimal
import json
import os
from datetime import datetime
import uuid
from datetime import datetime, timedelta  # Add timedelta here

# Initialize DynamoDB resource with error handling
try:
    dynamodb = boto3.resource(
        "dynamodb",
        region_name="us-east-1",
        aws_access_key_id=None,
        aws_secret_access_key=None,
    )
    DYNAMODB_AVAILABLE = True
    print("AWS DynamoDB connection established")
except Exception as e:
    print(f"Warning: Could not connect to AWS DynamoDB - {e}")
    print("Falling back to mock database for testing")
    DYNAMODB_AVAILABLE = False
    dynamodb = None

# Table names
USERS_TABLE = "blissful_users"
ROOMS_TABLE = "blissful_rooms"
BOOKINGS_TABLE = "blissful_bookings"
REVIEWS_TABLE = "blissful_reviews"
BRANCHES_TABLE = "blissful_branches"  # Multi-branch support
LOYALTY_TABLE = "blissful_loyalty"  # Cross-branch loyalty program
CHAT_MESSAGES_TABLE = "blissful_chat_messages"  # Chat messages
CHAT_REQUESTS_TABLE = "blissful_chat_requests"  # Chat requests (booking, reviews, reports, extra services)
PRICING_RULES_TABLE = "blissful_pricing_rules"  # Dynamic pricing rules
GUEST_PREFERENCES_TABLE = "blissful_guest_preferences"  # Guest preferences and history
WAITLIST_TABLE = "blissful_waitlist"  # Waitlist for unavailable rooms
SERVICES_TABLE = "blissful_services"  # Integrated service bookings
SERVICE_BOOKINGS_TABLE = "blissful_service_bookings"  # Service booking records
NOTIFICATIONS_TABLE = "blissful_notifications"  # Automated notifications queue

# Mock data storage for testing
mock_users = []
mock_rooms = []
mock_bookings = []
mock_reviews = []
mock_branches = []  # Add branches mock data
mock_loyalty = []  # Add loyalty mock data
mock_favorites = []  # Favorite rooms for users
mock_chat_messages = []  # Chat messages mock data
mock_chat_requests = []  # Chat requests mock data
mock_pricing_rules = []  # Dynamic pricing rules
mock_guest_preferences = []  # Guest preferences
mock_waitlist = []  # Waitlist entries
mock_services = []  # Available services
mock_service_bookings = []  # Service bookings
mock_notifications = []  # Notification queue


class DecimalEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, Decimal):
            return float(obj)
        return super(DecimalEncoder, self).default(obj)


def convert_floats_to_decimal(obj):
    """Recursively convert all float values to Decimal for DynamoDB compatibility"""
    if isinstance(obj, dict):
        return {k: convert_floats_to_decimal(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [convert_floats_to_decimal(item) for item in obj]
    elif isinstance(obj, float):
        return Decimal(str(obj))
    return obj


def create_tables():
    """Create DynamoDB tables if they don't exist"""
    if not DYNAMODB_AVAILABLE:
        print("Using mock database (no AWS connection)")
        return True

    try:
        # Check if tables already exist
        existing_tables = list(dynamodb.tables.all())
        existing_table_names = [table.name for table in existing_tables]

        # Chat Messages table
        if CHAT_MESSAGES_TABLE not in existing_table_names:
            chat_messages_table = dynamodb.create_table(
                TableName=CHAT_MESSAGES_TABLE,
                KeySchema=[{"AttributeName": "message_id", "KeyType": "HASH"}],
                AttributeDefinitions=[
                    {"AttributeName": "message_id", "AttributeType": "S"},
                    {"AttributeName": "user_id", "AttributeType": "S"},
                    {"AttributeName": "timestamp", "AttributeType": "S"},
                ],
                GlobalSecondaryIndexes=[
                    {
                        "IndexName": "UserMessagesIndex",
                        "KeySchema": [
                            {"AttributeName": "user_id", "KeyType": "HASH"},
                            {"AttributeName": "timestamp", "KeyType": "RANGE"},
                        ],
                        "Projection": {"ProjectionType": "ALL"},
                        "ProvisionedThroughput": {
                            "ReadCapacityUnits": 5,
                            "WriteCapacityUnits": 5,
                        },
                    }
                ],
                ProvisionedThroughput={"ReadCapacityUnits": 5, "WriteCapacityUnits": 5},
            )
            chat_messages_table.wait_until_exists()
            print(f"Created table: {CHAT_MESSAGES_TABLE}")
        else:
            print(f"Table {CHAT_MESSAGES_TABLE} already exists")

        # Chat Requests table (for booking, reviews, reports, extra services)
        if CHAT_REQUESTS_TABLE not in existing_table_names:
            chat_requests_table = dynamodb.create_table(
                TableName=CHAT_REQUESTS_TABLE,
                KeySchema=[{"AttributeName": "request_id", "KeyType": "HASH"}],
                AttributeDefinitions=[
                    {"AttributeName": "request_id", "AttributeType": "S"},
                    {"AttributeName": "user_id", "AttributeType": "S"},
                    {"AttributeName": "status", "AttributeType": "S"},
                    {"AttributeName": "request_type", "AttributeType": "S"},
                ],
                GlobalSecondaryIndexes=[
                    {
                        "IndexName": "UserRequestsIndex",
                        "KeySchema": [{"AttributeName": "user_id", "KeyType": "HASH"}],
                        "Projection": {"ProjectionType": "ALL"},
                        "ProvisionedThroughput": {
                            "ReadCapacityUnits": 5,
                            "WriteCapacityUnits": 5,
                        },
                    },
                    {
                        "IndexName": "StatusTypeIndex",
                        "KeySchema": [
                            {"AttributeName": "status", "KeyType": "HASH"},
                            {"AttributeName": "request_type", "KeyType": "RANGE"},
                        ],
                        "Projection": {"ProjectionType": "ALL"},
                        "ProvisionedThroughput": {
                            "ReadCapacityUnits": 5,
                            "WriteCapacityUnits": 5,
                        },
                    },
                ],
                ProvisionedThroughput={"ReadCapacityUnits": 5, "WriteCapacityUnits": 5},
            )
            chat_requests_table.wait_until_exists()
            print(f"Created table: {CHAT_REQUESTS_TABLE}")
        else:
            print(f"Table {CHAT_REQUESTS_TABLE} already exists")

        # Users table
        if USERS_TABLE not in existing_table_names:
            users_table = dynamodb.create_table(
                TableName=USERS_TABLE,
                KeySchema=[{"AttributeName": "user_id", "KeyType": "HASH"}],
                AttributeDefinitions=[
                    {"AttributeName": "user_id", "AttributeType": "S"},
                    {"AttributeName": "email", "AttributeType": "S"},
                ],
                GlobalSecondaryIndexes=[
                    {
                        "IndexName": "EmailIndex",
                        "KeySchema": [{"AttributeName": "email", "KeyType": "HASH"}],
                        "Projection": {"ProjectionType": "ALL"},
                        "ProvisionedThroughput": {
                            "ReadCapacityUnits": 5,
                            "WriteCapacityUnits": 5,
                        },
                    }
                ],
                ProvisionedThroughput={"ReadCapacityUnits": 5, "WriteCapacityUnits": 5},
            )
            users_table.wait_until_exists()
            print(f"Created table: {USERS_TABLE}")
        else:
            print(f"Table {USERS_TABLE} already exists")

        # Rooms table
        if ROOMS_TABLE not in existing_table_names:
            rooms_table = dynamodb.create_table(
                TableName=ROOMS_TABLE,
                KeySchema=[{"AttributeName": "room_id", "KeyType": "HASH"}],
                AttributeDefinitions=[
                    {"AttributeName": "room_id", "AttributeType": "S"},
                    {"AttributeName": "availability", "AttributeType": "S"},
                    {"AttributeName": "location", "AttributeType": "S"},
                ],
                GlobalSecondaryIndexes=[
                    {
                        "IndexName": "AvailabilityIndex",
                        "KeySchema": [
                            {"AttributeName": "availability", "KeyType": "HASH"},
                            {"AttributeName": "location", "KeyType": "RANGE"},
                        ],
                        "Projection": {"ProjectionType": "ALL"},
                        "ProvisionedThroughput": {
                            "ReadCapacityUnits": 5,
                            "WriteCapacityUnits": 5,
                        },
                    }
                ],
                ProvisionedThroughput={"ReadCapacityUnits": 5, "WriteCapacityUnits": 5},
            )
            rooms_table.wait_until_exists()
            print(f"Created table: {ROOMS_TABLE}")
        else:
            print(f"Table {ROOMS_TABLE} already exists")

        # Bookings table
        if BOOKINGS_TABLE not in existing_table_names:
            bookings_table = dynamodb.create_table(
                TableName=BOOKINGS_TABLE,
                KeySchema=[{"AttributeName": "booking_id", "KeyType": "HASH"}],
                AttributeDefinitions=[
                    {"AttributeName": "booking_id", "AttributeType": "S"},
                    {"AttributeName": "user_id", "AttributeType": "S"},
                    {"AttributeName": "room_id", "AttributeType": "S"},
                ],
                GlobalSecondaryIndexes=[
                    {
                        "IndexName": "UserBookingsIndex",
                        "KeySchema": [{"AttributeName": "user_id", "KeyType": "HASH"}],
                        "Projection": {"ProjectionType": "ALL"},
                        "ProvisionedThroughput": {
                            "ReadCapacityUnits": 5,
                            "WriteCapacityUnits": 5,
                        },
                    },
                    {
                        "IndexName": "RoomBookingsIndex",
                        "KeySchema": [{"AttributeName": "room_id", "KeyType": "HASH"}],
                        "Projection": {"ProjectionType": "ALL"},
                        "ProvisionedThroughput": {
                            "ReadCapacityUnits": 5,
                            "WriteCapacityUnits": 5,
                        },
                    },
                ],
                ProvisionedThroughput={"ReadCapacityUnits": 5, "WriteCapacityUnits": 5},
            )
            bookings_table.wait_until_exists()
            print(f"Created table: {BOOKINGS_TABLE}")
        else:
            print(f"Table {BOOKINGS_TABLE} already exists")

        # Reviews table
        if REVIEWS_TABLE not in existing_table_names:
            reviews_table = dynamodb.create_table(
                TableName=REVIEWS_TABLE,
                KeySchema=[{"AttributeName": "review_id", "KeyType": "HASH"}],
                AttributeDefinitions=[
                    {"AttributeName": "review_id", "AttributeType": "S"},
                    {"AttributeName": "user_id", "AttributeType": "S"},
                    {"AttributeName": "room_id", "AttributeType": "S"},
                ],
                GlobalSecondaryIndexes=[
                    {
                        "IndexName": "UserReviewsIndex",
                        "KeySchema": [{"AttributeName": "user_id", "KeyType": "HASH"}],
                        "Projection": {"ProjectionType": "ALL"},
                        "ProvisionedThroughput": {
                            "ReadCapacityUnits": 5,
                            "WriteCapacityUnits": 5,
                        },
                    },
                    {
                        "IndexName": "RoomReviewsIndex",
                        "KeySchema": [{"AttributeName": "room_id", "KeyType": "HASH"}],
                        "Projection": {"ProjectionType": "ALL"},
                        "ProvisionedThroughput": {
                            "ReadCapacityUnits": 5,
                            "WriteCapacityUnits": 5,
                        },
                    },
                ],
                ProvisionedThroughput={"ReadCapacityUnits": 5, "WriteCapacityUnits": 5},
            )
            reviews_table.wait_until_exists()
            print(f"Created table: {REVIEWS_TABLE}")
        else:
            print(f"Table {REVIEWS_TABLE} already exists")

        # Branches table (Multi-branch support)
        if BRANCHES_TABLE not in existing_table_names:
            branches_table = dynamodb.create_table(
                TableName=BRANCHES_TABLE,
                KeySchema=[{"AttributeName": "branch_id", "KeyType": "HASH"}],
                AttributeDefinitions=[
                    {"AttributeName": "branch_id", "AttributeType": "S"},
                    {"AttributeName": "status", "AttributeType": "S"},
                    {"AttributeName": "city", "AttributeType": "S"},
                ],
                GlobalSecondaryIndexes=[
                    {
                        "IndexName": "StatusIndex",
                        "KeySchema": [
                            {"AttributeName": "status", "KeyType": "HASH"},
                            {"AttributeName": "city", "KeyType": "RANGE"},
                        ],
                        "Projection": {"ProjectionType": "ALL"},
                        "ProvisionedThroughput": {
                            "ReadCapacityUnits": 5,
                            "WriteCapacityUnits": 5,
                        },
                    }
                ],
                ProvisionedThroughput={"ReadCapacityUnits": 5, "WriteCapacityUnits": 5},
            )
            branches_table.wait_until_exists()
            print(f"Created table: {BRANCHES_TABLE}")
        else:
            print(f"Table {BRANCHES_TABLE} already exists")

        # Loyalty table (Cross-branch loyalty program)
        if LOYALTY_TABLE not in existing_table_names:
            loyalty_table = dynamodb.create_table(
                TableName=LOYALTY_TABLE,
                KeySchema=[{"AttributeName": "user_id", "KeyType": "HASH"}],
                AttributeDefinitions=[
                    {"AttributeName": "user_id", "AttributeType": "S"}
                ],
                ProvisionedThroughput={"ReadCapacityUnits": 5, "WriteCapacityUnits": 5},
            )
            loyalty_table.wait_until_exists()
            print(f"Created table: {LOYALTY_TABLE}")
        else:
            print(f"Table {LOYALTY_TABLE} already exists")

        # Pricing Rules table (Dynamic pricing)
        if PRICING_RULES_TABLE not in existing_table_names:
            pricing_rules_table = dynamodb.create_table(
                TableName=PRICING_RULES_TABLE,
                KeySchema=[{"AttributeName": "rule_id", "KeyType": "HASH"}],
                AttributeDefinitions=[
                    {"AttributeName": "rule_id", "AttributeType": "S"},
                    {"AttributeName": "rule_type", "AttributeType": "S"},
                    {"AttributeName": "branch_id", "AttributeType": "S"},
                ],
                GlobalSecondaryIndexes=[
                    {
                        "IndexName": "RuleTypeIndex",
                        "KeySchema": [
                            {"AttributeName": "rule_type", "KeyType": "HASH"}
                        ],
                        "Projection": {"ProjectionType": "ALL"},
                        "ProvisionedThroughput": {
                            "ReadCapacityUnits": 5,
                            "WriteCapacityUnits": 5,
                        },
                    },
                    {
                        "IndexName": "BranchRulesIndex",
                        "KeySchema": [
                            {"AttributeName": "branch_id", "KeyType": "HASH"}
                        ],
                        "Projection": {"ProjectionType": "ALL"},
                        "ProvisionedThroughput": {
                            "ReadCapacityUnits": 5,
                            "WriteCapacityUnits": 5,
                        },
                    },
                ],
                ProvisionedThroughput={"ReadCapacityUnits": 5, "WriteCapacityUnits": 5},
            )
            pricing_rules_table.wait_until_exists()
            print(f"Created table: {PRICING_RULES_TABLE}")
        else:
            print(f"Table {PRICING_RULES_TABLE} already exists")

        # Guest Preferences table
        if GUEST_PREFERENCES_TABLE not in existing_table_names:
            guest_preferences_table = dynamodb.create_table(
                TableName=GUEST_PREFERENCES_TABLE,
                KeySchema=[{"AttributeName": "user_id", "KeyType": "HASH"}],
                AttributeDefinitions=[
                    {"AttributeName": "user_id", "AttributeType": "S"}
                ],
                ProvisionedThroughput={"ReadCapacityUnits": 5, "WriteCapacityUnits": 5},
            )
            guest_preferences_table.wait_until_exists()
            print(f"Created table: {GUEST_PREFERENCES_TABLE}")
        else:
            print(f"Table {GUEST_PREFERENCES_TABLE} already exists")

        # Waitlist table
        if WAITLIST_TABLE not in existing_table_names:
            waitlist_table = dynamodb.create_table(
                TableName=WAITLIST_TABLE,
                KeySchema=[{"AttributeName": "waitlist_id", "KeyType": "HASH"}],
                AttributeDefinitions=[
                    {"AttributeName": "waitlist_id", "AttributeType": "S"},
                    {"AttributeName": "user_id", "AttributeType": "S"},
                    {"AttributeName": "room_id", "AttributeType": "S"},
                    {"AttributeName": "status", "AttributeType": "S"},
                ],
                GlobalSecondaryIndexes=[
                    {
                        "IndexName": "UserWaitlistIndex",
                        "KeySchema": [{"AttributeName": "user_id", "KeyType": "HASH"}],
                        "Projection": {"ProjectionType": "ALL"},
                        "ProvisionedThroughput": {
                            "ReadCapacityUnits": 5,
                            "WriteCapacityUnits": 5,
                        },
                    },
                    {
                        "IndexName": "RoomWaitlistIndex",
                        "KeySchema": [{"AttributeName": "room_id", "KeyType": "HASH"}],
                        "Projection": {"ProjectionType": "ALL"},
                        "ProvisionedThroughput": {
                            "ReadCapacityUnits": 5,
                            "WriteCapacityUnits": 5,
                        },
                    },
                    {
                        "IndexName": "StatusIndex",
                        "KeySchema": [{"AttributeName": "status", "KeyType": "HASH"}],
                        "Projection": {"ProjectionType": "ALL"},
                        "ProvisionedThroughput": {
                            "ReadCapacityUnits": 5,
                            "WriteCapacityUnits": 5,
                        },
                    },
                ],
                ProvisionedThroughput={"ReadCapacityUnits": 5, "WriteCapacityUnits": 5},
            )
            waitlist_table.wait_until_exists()
            print(f"Created table: {WAITLIST_TABLE}")
        else:
            print(f"Table {WAITLIST_TABLE} already exists")

        # Services table (spa, restaurant, transportation, etc.)
        if SERVICES_TABLE not in existing_table_names:
            services_table = dynamodb.create_table(
                TableName=SERVICES_TABLE,
                KeySchema=[{"AttributeName": "service_id", "KeyType": "HASH"}],
                AttributeDefinitions=[
                    {"AttributeName": "service_id", "AttributeType": "S"},
                    {"AttributeName": "branch_id", "AttributeType": "S"},
                    {"AttributeName": "service_type", "AttributeType": "S"},
                ],
                GlobalSecondaryIndexes=[
                    {
                        "IndexName": "BranchServicesIndex",
                        "KeySchema": [
                            {"AttributeName": "branch_id", "KeyType": "HASH"}
                        ],
                        "Projection": {"ProjectionType": "ALL"},
                        "ProvisionedThroughput": {
                            "ReadCapacityUnits": 5,
                            "WriteCapacityUnits": 5,
                        },
                    },
                    {
                        "IndexName": "ServiceTypeIndex",
                        "KeySchema": [
                            {"AttributeName": "service_type", "KeyType": "HASH"}
                        ],
                        "Projection": {"ProjectionType": "ALL"},
                        "ProvisionedThroughput": {
                            "ReadCapacityUnits": 5,
                            "WriteCapacityUnits": 5,
                        },
                    },
                ],
                ProvisionedThroughput={"ReadCapacityUnits": 5, "WriteCapacityUnits": 5},
            )
            services_table.wait_until_exists()
            print(f"Created table: {SERVICES_TABLE}")
        else:
            print(f"Table {SERVICES_TABLE} already exists")

        # Service Bookings table
        if SERVICE_BOOKINGS_TABLE not in existing_table_names:
            service_bookings_table = dynamodb.create_table(
                TableName=SERVICE_BOOKINGS_TABLE,
                KeySchema=[{"AttributeName": "service_booking_id", "KeyType": "HASH"}],
                AttributeDefinitions=[
                    {"AttributeName": "service_booking_id", "AttributeType": "S"},
                    {"AttributeName": "user_id", "AttributeType": "S"},
                    {"AttributeName": "booking_id", "AttributeType": "S"},
                ],
                GlobalSecondaryIndexes=[
                    {
                        "IndexName": "UserServiceBookingsIndex",
                        "KeySchema": [{"AttributeName": "user_id", "KeyType": "HASH"}],
                        "Projection": {"ProjectionType": "ALL"},
                        "ProvisionedThroughput": {
                            "ReadCapacityUnits": 5,
                            "WriteCapacityUnits": 5,
                        },
                    },
                    {
                        "IndexName": "BookingServicesIndex",
                        "KeySchema": [
                            {"AttributeName": "booking_id", "KeyType": "HASH"}
                        ],
                        "Projection": {"ProjectionType": "ALL"},
                        "ProvisionedThroughput": {
                            "ReadCapacityUnits": 5,
                            "WriteCapacityUnits": 5,
                        },
                    },
                ],
                ProvisionedThroughput={"ReadCapacityUnits": 5, "WriteCapacityUnits": 5},
            )
            service_bookings_table.wait_until_exists()
            print(f"Created table: {SERVICE_BOOKINGS_TABLE}")
        else:
            print(f"Table {SERVICE_BOOKINGS_TABLE} already exists")

        # Notifications table (for automated reminders)
        if NOTIFICATIONS_TABLE not in existing_table_names:
            notifications_table = dynamodb.create_table(
                TableName=NOTIFICATIONS_TABLE,
                KeySchema=[{"AttributeName": "notification_id", "KeyType": "HASH"}],
                AttributeDefinitions=[
                    {"AttributeName": "notification_id", "AttributeType": "S"},
                    {"AttributeName": "user_id", "AttributeType": "S"},
                    {"AttributeName": "status", "AttributeType": "S"},
                ],
                GlobalSecondaryIndexes=[
                    {
                        "IndexName": "UserNotificationsIndex",
                        "KeySchema": [{"AttributeName": "user_id", "KeyType": "HASH"}],
                        "Projection": {"ProjectionType": "ALL"},
                        "ProvisionedThroughput": {
                            "ReadCapacityUnits": 5,
                            "WriteCapacityUnits": 5,
                        },
                    },
                    {
                        "IndexName": "StatusIndex",
                        "KeySchema": [{"AttributeName": "status", "KeyType": "HASH"}],
                        "Projection": {"ProjectionType": "ALL"},
                        "ProvisionedThroughput": {
                            "ReadCapacityUnits": 5,
                            "WriteCapacityUnits": 5,
                        },
                    },
                ],
                ProvisionedThroughput={"ReadCapacityUnits": 5, "WriteCapacityUnits": 5},
            )
            notifications_table.wait_until_exists()
            print(f"Created table: {NOTIFICATIONS_TABLE}")
        else:
            print(f"Table {NOTIFICATIONS_TABLE} already exists")

        print(f"All tables created or already exist")
        return True

    except Exception as e:
        print(f"Error creating tables: {e}")
        print("Falling back to mock database")
        return False


# Helper function to get table
def get_table(table_name):
    if DYNAMODB_AVAILABLE:
        try:
            return dynamodb.Table(table_name)
        except Exception as e:
            print(f"Error accessing table {table_name}: {e}")
            return None
    return None


# User operations
def add_user(user_data):
    if DYNAMODB_AVAILABLE:
        try:
            table = get_table(USERS_TABLE)
            if table:
                response = table.put_item(Item=user_data)
                return response
        except Exception as e:
            print(f"Error adding user to DynamoDB: {e}")

    # Fallback to mock database
    mock_users.append(user_data)
    return {"ResponseMetadata": {"HTTPStatusCode": 200}}


def get_user(email_or_id):
    """Get user by email or user_id"""
    if DYNAMODB_AVAILABLE:
        try:
            table = get_table(USERS_TABLE)
            if table:
                # Try email first
                for item in table.scan()["Items"]:
                    if (
                        item.get("email") == email_or_id
                        or item.get("user_id") == email_or_id
                    ):
                        return item
                return None
        except Exception as e:
            print(f"Error getting user from DynamoDB: {e}")

    # Fallback to mock database
    for user in mock_users:
        if user.get("email") == email_or_id or user.get("user_id") == email_or_id:
            return user
    return None


def get_all_users():
    if DYNAMODB_AVAILABLE:
        try:
            table = get_table(USERS_TABLE)
            if table:
                response = table.scan()
                return response.get("Items", [])
        except Exception as e:
            print(f"Error getting all users from DynamoDB: {e}")

    return mock_users


def delete_user(user_id):
    if DYNAMODB_AVAILABLE:
        try:
            table = get_table(USERS_TABLE)
            if table:
                response = table.delete_item(Key={"user_id": user_id})
                return response
        except Exception as e:
            print(f"Error deleting user from DynamoDB: {e}")

    # Fallback to mock database
    global mock_users
    mock_users = [u for u in mock_users if u.get("user_id") != user_id]
    return {"ResponseMetadata": {"HTTPStatusCode": 200}}


def update_user(user_id, update_data):
    """Update user fields (name, email, role, age, phone, password, branch_id, etc)."""
    # Never allow changing user_id via update_data
    safe_update = {k: v for k, v in (update_data or {}).items() if k != "user_id"}

    if DYNAMODB_AVAILABLE:
        try:
            table = get_table(USERS_TABLE)
            if table:
                # Build update expression dynamically
                update_expr = "SET "
                expr_attrs = {}
                expr_names = {}

                for key, value in safe_update.items():
                    update_expr += f"#{key} = :{key}, "
                    expr_names[f"#{key}"] = key
                    expr_attrs[f":{key}"] = value

                update_expr = update_expr.rstrip(", ")
                if update_expr == "SET":
                    return {"ResponseMetadata": {"HTTPStatusCode": 200}}

                response = table.update_item(
                    Key={"user_id": user_id},
                    UpdateExpression=update_expr,
                    ExpressionAttributeNames=expr_names,
                    ExpressionAttributeValues=expr_attrs,
                )
                return response
        except Exception as e:
            print(f"Error updating user in DynamoDB: {e}")

    # Fallback to mock database
    for user in mock_users:
        if user.get("user_id") == user_id:
            user.update(safe_update)
            break
    return {"ResponseMetadata": {"HTTPStatusCode": 200}}


# Room operations
def add_room(room_data):
    if DYNAMODB_AVAILABLE:
        try:
            table = get_table(ROOMS_TABLE)
            if table:
                # Convert floats to Decimal for DynamoDB
                room_data = convert_floats_to_decimal(room_data)
                response = table.put_item(Item=room_data)
                return response
        except Exception as e:
            print(f"Error adding room to DynamoDB: {e}")

    # Fallback to mock database
    mock_rooms.append(room_data)
    return {"ResponseMetadata": {"HTTPStatusCode": 200}}


def get_rooms(location=None, availability="available", branch_id=None):
    """Get rooms with optional filters for location, availability, and branch_id"""
    if DYNAMODB_AVAILABLE:
        try:
            table = get_table(ROOMS_TABLE)
            if table:
                if availability:
                    # Filter by availability
                    try:
                        if location:
                            response = table.query(
                                IndexName="AvailabilityIndex",
                                KeyConditionExpression=Key("availability").eq(
                                    availability
                                )
                                & Key("location").begins_with(location),
                            )
                        else:
                            response = table.query(
                                IndexName="AvailabilityIndex",
                                KeyConditionExpression=Key("availability").eq(
                                    availability
                                ),
                            )
                        items = response.get("Items", [])
                    except ClientError as e:
                        if e.response["Error"]["Code"] == "ValidationException":
                            # Fallback to scan if index doesn't exist
                            print(
                                f"Index 'AvailabilityIndex' not found, falling back to scan: {e}"
                            )
                            response = table.scan(
                                FilterExpression=Attr("availability").eq(availability)
                            )
                            items = response.get("Items", [])
                            if location:
                                items = [
                                    r
                                    for r in items
                                    if location.lower() in r.get("location", "").lower()
                                ]
                        else:
                            raise e
                else:
                    # Get all rooms regardless of availability
                    response = table.scan()
                    items = response.get("Items", [])
                    if location:
                        items = [
                            r
                            for r in items
                            if location.lower() in r.get("location", "").lower()
                        ]

                # Filter by branch_id if provided
                if branch_id:
                    items = [r for r in items if r.get("branch_id") == branch_id]
                return items
        except Exception as e:
            print(f"Error getting rooms from DynamoDB: {e}")

    # Fallback to mock database
    rooms = []
    for room in mock_rooms:
        # Filter by availability if specified
        if availability and room.get("availability") != availability:
            continue
        # Filter by branch_id if provided
        if branch_id and room.get("branch_id") != branch_id:
            continue
        if not location or location.lower() in room.get("location", "").lower():
            rooms.append(room)
    return rooms


def get_all_rooms(branch_id=None):
    """Get all rooms, optionally filtered by branch_id"""
    if DYNAMODB_AVAILABLE:
        try:
            table = get_table(ROOMS_TABLE)
            if table:
                items = []
                response = table.scan()
                items.extend(response.get("Items", []))

                # Handle pagination
                while "LastEvaluatedKey" in response:
                    try:
                        response = table.scan(
                            ExclusiveStartKey=response["LastEvaluatedKey"]
                        )
                        items.extend(response.get("Items", []))
                    except Exception as e:
                        print(f"Error during pagination scan: {e}")
                        break

                # Filter by branch_id if provided
                if branch_id:
                    items = [r for r in items if r.get("branch_id") == branch_id]
                return items
        except Exception as e:
            print(f"Error getting all rooms from DynamoDB: {e}")
            # If we are strictly in AWS mode, we should perhaps return the partial list or raise.
            # But returning mock_rooms (which is empty) causes the init script to think DB is empty.
            # Safer to return what we have or empty list, NOT failover to mock_rooms if we wanted real data.
            # But to be safe against the 're-population' bug, let's return a non-empty list if possible, or re-raise
            if "Table not found" not in str(e):
                # If it's a connection error, we don't want to trigger population
                return []

    # Filter mock rooms by branch_id if provided
    if branch_id:
        return [r for r in mock_rooms if r.get("branch_id") == branch_id]
    return mock_rooms


def get_room(room_id):
    if DYNAMODB_AVAILABLE:
        try:
            table = get_table(ROOMS_TABLE)
            if table:
                response = table.get_item(Key={"room_id": room_id})
                return response.get("Item")
        except Exception as e:
            print(f"Error getting room from DynamoDB: {e}")

    # Fallback to mock database
    for room in mock_rooms:
        if room.get("room_id") == room_id:
            return room
    return None


def update_room_availability(room_id, availability):
    if DYNAMODB_AVAILABLE:
        try:
            table = get_table(ROOMS_TABLE)
            if table:
                response = table.update_item(
                    Key={"room_id": room_id},
                    UpdateExpression="SET availability = :avail",
                    ExpressionAttributeValues={":avail": availability},
                )
                return response
        except Exception as e:
            print(f"Error updating room in DynamoDB: {e}")

    # Fallback to mock database
    for room in mock_rooms:
        if room.get("room_id") == room_id:
            room["availability"] = availability
            break
    return {"ResponseMetadata": {"HTTPStatusCode": 200}}


def delete_room(room_id):
    if DYNAMODB_AVAILABLE:
        try:
            table = get_table(ROOMS_TABLE)
            if table:
                response = table.delete_item(Key={"room_id": room_id})
                return response
        except Exception as e:
            print(f"Error deleting room from DynamoDB: {e}")

    # Fallback to mock database
    global mock_rooms
    mock_rooms = [r for r in mock_rooms if r.get("room_id") != room_id]
    return {"ResponseMetadata": {"HTTPStatusCode": 200}}


def update_room(room_data):
    """Update a room (expects room_id present in room_data)."""
    room_id = (room_data or {}).get("room_id")
    if not room_id:
        raise ValueError("room_id is required to update room")

    # Never allow changing room_id via update
    safe_update = {k: v for k, v in (room_data or {}).items() if k != "room_id"}

    if DYNAMODB_AVAILABLE:
        try:
            table = get_table(ROOMS_TABLE)
            if table:
                update_expr = "SET "
                expr_attrs = {}
                expr_names = {}

                for key, value in safe_update.items():
                    update_expr += f"#{key} = :{key}, "
                    expr_names[f"#{key}"] = key
                    # Convert floats to Decimal for DynamoDB
                    expr_attrs[f":{key}"] = convert_floats_to_decimal(value)

                update_expr = update_expr.rstrip(", ")
                if update_expr == "SET":
                    return {"ResponseMetadata": {"HTTPStatusCode": 200}}

                response = table.update_item(
                    Key={"room_id": room_id},
                    UpdateExpression=update_expr,
                    ExpressionAttributeNames=expr_names,
                    ExpressionAttributeValues=expr_attrs,
                )
                return response
        except Exception as e:
            print(f"Error updating room in DynamoDB: {e}")

    # Fallback to mock database
    for room in mock_rooms:
        if room.get("room_id") == room_id:
            room.update(safe_update)
            break
    return {"ResponseMetadata": {"HTTPStatusCode": 200}}


# Booking operations
def add_booking(booking_data):
    if DYNAMODB_AVAILABLE:
        try:
            table = get_table(BOOKINGS_TABLE)
            if table:
                response = table.put_item(Item=booking_data)
                return response
        except Exception as e:
            print(f"Error adding booking to DynamoDB: {e}")

    # Fallback to mock database
    mock_bookings.append(booking_data)
    return {"ResponseMetadata": {"HTTPStatusCode": 200}}


def get_user_bookings(user_id):
    print(f"DEBUG get_user_bookings: Querying for user_id={user_id}")
    if DYNAMODB_AVAILABLE:
        try:
            table = get_table(BOOKINGS_TABLE)
            if table:
                print(f"DEBUG: Querying UserBookingsIndex for user_id={user_id}")
                response = table.query(
                    IndexName="UserBookingsIndex",
                    KeyConditionExpression=Key("user_id").eq(user_id),
                )
                bookings = response.get("Items", [])
                print(
                    f"DEBUG: Found {len(bookings)} bookings in DynamoDB for user {user_id}"
                )
                return [normalize_booking(b) for b in bookings]
        except Exception as e:
            print(f"Error getting user bookings from DynamoDB: {e}")

            # Fallback to scan if index is missing
            if "ValidationException" in str(
                e
            ) or "The table does not have the specified index" in str(e):
                print("DEBUG: Index missing, falling back to SCAN for user bookings")
                try:
                    response = table.scan(FilterExpression=Attr("user_id").eq(user_id))
                    bookings = response.get("Items", [])
                    return [normalize_booking(b) for b in bookings]
                except Exception as scan_e:
                    print(f"Error scanning bookings: {scan_e}")

            import traceback

            traceback.print_exc()

    # Fallback to mock database
    print(
        f"DEBUG: Falling back to mock database (DYNAMODB_AVAILABLE={DYNAMODB_AVAILABLE})"
    )
    bookings = []
    for booking in mock_bookings:
        if booking.get("user_id") == user_id:
            bookings.append(normalize_booking(booking))
    return bookings


def get_all_bookings():
    """Get all bookings"""
    if DYNAMODB_AVAILABLE:
        try:
            table = get_table(BOOKINGS_TABLE)
            if table:
                response = table.scan()
                bookings = response.get("Items", [])
                return [normalize_booking(b) for b in bookings]
        except Exception as e:
            print(f"Error getting all bookings from DynamoDB: {e}")

    return [normalize_booking(b) for b in mock_bookings]


def get_booking(booking_id):
    """Get a single booking by booking_id"""
    if DYNAMODB_AVAILABLE:
        try:
            table = get_table(BOOKINGS_TABLE)
            if table:
                response = table.get_item(Key={"booking_id": booking_id})
                return response.get("Item")
        except Exception as e:
            print(f"Error getting booking from DynamoDB: {e}")

    # Fallback to mock database
    for booking in mock_bookings:
        if booking.get("booking_id") == booking_id:
            return booking
    return None


def update_booking_status(booking_id, status):
    """Update booking status fields (status & booking_status)"""
    if DYNAMODB_AVAILABLE:
        try:
            table = get_table(BOOKINGS_TABLE)
            if table:
                response = table.update_item(
                    Key={"booking_id": booking_id},
                    UpdateExpression="SET #s = :s, booking_status = :s",
                    ExpressionAttributeNames={"#s": "status"},
                    ExpressionAttributeValues={":s": status},
                )
                return response
        except Exception as e:
            print(f"Error updating booking in DynamoDB: {e}")

    # Fallback to mock database
    for booking in mock_bookings:
        if booking.get("booking_id") == booking_id:
            booking["status"] = status
            booking["booking_status"] = status
            break
    return {"ResponseMetadata": {"HTTPStatusCode": 200}}


def delete_booking(booking_id):
    """Delete a booking by booking_id"""
    if DYNAMODB_AVAILABLE:
        try:
            table = get_table(BOOKINGS_TABLE)
            if table:
                response = table.delete_item(Key={"booking_id": booking_id})
                return response
        except Exception as e:
            print(f"Error deleting booking from DynamoDB: {e}")

    # Fallback to mock database
    global mock_bookings
    mock_bookings = [b for b in mock_bookings if b.get("booking_id") != booking_id]
    return {"ResponseMetadata": {"HTTPStatusCode": 200}}


def get_room_bookings(room_id):
    if DYNAMODB_AVAILABLE:
        try:
            table = get_table(BOOKINGS_TABLE)
            if table:
                response = table.query(
                    IndexName="RoomBookingsIndex",
                    KeyConditionExpression=Key("room_id").eq(room_id),
                )
                return response.get("Items", [])
        except Exception as e:
            print(f"Error getting room bookings from DynamoDB: {e}")

    # Fallback to mock database
    bookings = []
    for booking in mock_bookings:
        if booking.get("room_id") == room_id:
            bookings.append(booking)
    return bookings


# Review operations
def add_review(review_data):
    """Add a guest review"""
    if DYNAMODB_AVAILABLE:
        try:
            # Note: Create REVIEWS_TABLE = 'blissful_reviews' in DynamoDB
            table = dynamodb.Table("blissful_reviews")
            response = table.put_item(Item=review_data)
            return response
        except Exception as e:
            print(f"Error adding review to DynamoDB: {e}")

    # Fallback to mock database
    mock_reviews.append(review_data)
    return {"ResponseMetadata": {"HTTPStatusCode": 200}}


def get_room_reviews(room_id):
    """Get all reviews for a specific room"""
    if DYNAMODB_AVAILABLE:
        try:
            table = dynamodb.Table("blissful_reviews")
            response = table.query(
                IndexName="RoomReviewsIndex",
                KeyConditionExpression=Key("room_id").eq(room_id),
            )
            return response.get("Items", [])
        except Exception as e:
            print(f"Error getting room reviews from DynamoDB: {e}")

    # Fallback to mock database
    reviews = []
    for review in mock_reviews:
        if review.get("room_id") == room_id:
            reviews.append(review)
    return reviews


def get_user_reviews(user_id):
    """Get all reviews submitted by a user"""
    if DYNAMODB_AVAILABLE:
        try:
            table = dynamodb.Table("blissful_reviews")
            response = table.query(
                IndexName="UserReviewsIndex",
                KeyConditionExpression=Key("user_id").eq(user_id),
            )
            return response.get("Items", [])
        except Exception as e:
            print(f"Error getting user reviews from DynamoDB: {e}")

            # Fallback to scan if index is missing
            if "ValidationException" in str(
                e
            ) or "The table does not have the specified index" in str(e):
                try:
                    response = table.scan(FilterExpression=Attr("user_id").eq(user_id))
                    return response.get("Items", [])
                except Exception as scan_e:
                    print(f"Error scanning reviews: {scan_e}")

    # Fallback to mock database
    reviews = []
    for review in mock_reviews:
        if review.get("user_id") == user_id:
            reviews.append(review)
    return reviews


def get_all_reviews():
    """Get all reviews"""
    if DYNAMODB_AVAILABLE:
        try:
            table = dynamodb.Table("blissful_reviews")
            response = table.scan()
            return response.get("Items", [])
        except Exception as e:
            print(f"Error getting all reviews from DynamoDB: {e}")

    return mock_reviews


# Analytics functions
def get_analytics():
    """Get analytics data for admin dashboard"""
    analytics = {
        "users": {"total": 0, "by_role": {}},
        "rooms": {"total": 0, "by_availability": {}, "by_type": {}},
        "bookings": {"total": 0, "by_status": {}},
    }

    try:
        # User analytics
        users = get_all_users()
        analytics["users"]["total"] = len(users)
        for user in users:
            role = user.get("role", "unknown")
            analytics["users"]["by_role"][role] = (
                analytics["users"]["by_role"].get(role, 0) + 1
            )

        # Room analytics
        rooms = get_all_rooms()
        analytics["rooms"]["total"] = len(rooms)
        for room in rooms:
            availability = room.get("availability", "unknown")
            analytics["rooms"]["by_availability"][availability] = (
                analytics["rooms"]["by_availability"].get(availability, 0) + 1
            )

            room_type = room.get("room_type", "unknown")
            analytics["rooms"]["by_type"][room_type] = (
                analytics["rooms"]["by_type"].get(room_type, 0) + 1
            )

        # Booking analytics
        bookings = get_all_bookings()
        analytics["bookings"]["total"] = len(bookings)
        for booking in bookings:
            status = booking.get("status", "unknown")
            analytics["bookings"]["by_status"][status] = (
                analytics["bookings"]["by_status"].get(status, 0) + 1
            )

    except Exception as e:
        print(f"Analytics error: {e}")
        # Return empty analytics structure
        analytics = {
            "users": {"total": 0, "by_role": {}},
            "rooms": {"total": 0, "by_availability": {}, "by_type": {}},
            "bookings": {"total": 0, "by_status": {}},
        }

    return analytics


# Add sample data for testing
def add_sample_data():
    """Add sample data for testing"""
    try:
        if not mock_users and not mock_rooms and not mock_bookings:
            import hashlib

            def hash_password(password):
                """Hash password using SHA256"""
                return hashlib.sha256(password.encode()).hexdigest()

            sample_users = [
                {
                    "user_id": str(uuid.uuid4()),
                    "name": "Ajith Kumar",
                    "email": "ajithkumar3108200@gmail.com",
                    "password": hash_password("Ajith@31"),
                    "age": 25,
                    "role": "guest",
                    "phone": "+91-98765-43210",
                    "created_at": datetime.now().isoformat(),
                },
                {
                    "user_id": str(uuid.uuid4()),
                    "name": "Staff Member",
                    "email": "staff1@example.com",
                    "password": hash_password("password123"),
                    "age": 30,
                    "role": "staff",
                    "phone": "+91-97654-32109",
                    "created_at": datetime.now().isoformat(),
                },
                {
                    "user_id": str(uuid.uuid4()),
                    "name": "Admin User",
                    "email": "admin@example.com",
                    "password": hash_password("password123"),
                    "age": 35,
                    "role": "admin",
                    "phone": "+91-96543-21098",
                    "created_at": datetime.now().isoformat(),
                },
            ]

            sample_bookings = [
                {
                    "booking_id": str(uuid.uuid4()),
                    "user_id": sample_users[0]["user_id"],
                    "room_id": "",  # Will be filled after rooms are created
                    "check_in": (datetime.now() + timedelta(days=7)).strftime(
                        "%Y-%m-%d"
                    ),
                    "check_out": (datetime.now() + timedelta(days=14)).strftime(
                        "%Y-%m-%d"
                    ),
                    "status": "confirmed",
                    "created_at": datetime.now().isoformat(),
                    "guest_name": sample_users[0]["name"],
                    "guest_email": sample_users[0]["email"],
                }
            ]

            mock_users.extend(sample_users)
            mock_bookings.extend(sample_bookings)

            print("=" * 70)
            print("SAMPLE DATA GENERATED SUCCESSFULLY")
            print("=" * 70)
            print(f"Total Users: {len(sample_users)}")
            print(f"Total Rooms: {len(mock_rooms)}")
            print("\nRoom Distribution:")
            print("  • Single Rooms: 30")
            print("  • Double Rooms: 30")
            print("  • Family Suites: 20")
            print("  • Couple Rooms: 10")
            print("  • VIP Suites: 10")
            print("  • TOTAL: 100+ rooms")
            print("\nCurrency: Indian Rupee (₹)")
            print("Phone Format: +91-XXXXX-XXXXX")
            print("\nTest Accounts:")
            print("  👤 Guest: ajithkumar3108200@gmail.com / Ajith@31")
            print("  👨‍💼 Staff: staff1@example.com / password123")
            print("  👨‍💻 Admin: admin@example.com / password123")
            print("=" * 70)

    except Exception as e:
        print(f"Error adding sample data: {e}")


def create_user(email, password, name="", age=18, role="guest"):
    """Create a new user with hashed password"""
    try:
        user_data = {
            "user_id": str(uuid.uuid4()),
            "name": name,
            "email": email.lower(),
            "password": password,  # In production, hash this
            "age": age,
            "role": role,
            "created_at": datetime.now().isoformat(),
        }
        add_user(user_data)
        return user_data
    except Exception as e:
        print(f"Error creating user: {e}")
        return None


def get_user_by_email(email):
    """Retrieve user by email with their role"""
    return get_user(email.lower())


def get_room_rating(room_id):
    """Calculate average rating for a room"""
    reviews = get_room_reviews(room_id)
    if not reviews:
        return 0

    total_rating = sum(float(review.get("rating", 0)) for review in reviews)
    return round(total_rating / len(reviews), 1)


# Branch operations (Multi-branch support)
def add_branch(branch_data):
    """Add a new branch"""
    if DYNAMODB_AVAILABLE:
        try:
            table = get_table(BRANCHES_TABLE)
            if table:
                # Convert floats to Decimal for DynamoDB
                branch_data = convert_floats_to_decimal(branch_data)
                response = table.put_item(Item=branch_data)
                return response
        except Exception as e:
            print(f"Error adding branch to DynamoDB: {e}")

    # Fallback to mock database
    mock_branches.append(branch_data)
    return {"ResponseMetadata": {"HTTPStatusCode": 200}}


def get_branch(branch_id):
    """Get branch by branch_id"""
    if DYNAMODB_AVAILABLE:
        try:
            table = get_table(BRANCHES_TABLE)
            if table:
                response = table.get_item(Key={"branch_id": branch_id})
                return response.get("Item")
        except Exception as e:
            print(f"Error getting branch from DynamoDB: {e}")

    # Fallback to mock database
    for branch in mock_branches:
        if branch.get("branch_id") == branch_id:
            return branch
    return None


def get_all_branches(status="active"):
    """Get all branches, optionally filtered by status"""
    if DYNAMODB_AVAILABLE:
        try:
            table = get_table(BRANCHES_TABLE)
            if table:
                # Use scan instead of query since StatusIndex may not exist
                response = table.scan()
                branches = response.get("Items", [])

                # Filter by status if provided
                if status:
                    branches = [b for b in branches if b.get("status") == status]

                return branches
        except Exception as e:
            print(f"Error getting branches from DynamoDB: {e}")
            import traceback

            traceback.print_exc()

    # Fallback to mock database
    if status:
        return [b for b in mock_branches if b.get("status") == status]
    return mock_branches


def get_branch_by_city(city):
    """Get branch by city name"""
    branches = get_all_branches()
    for branch in branches:
        branch_city = (
            branch.get("location", {}).get("city", "")
            if isinstance(branch.get("location"), dict)
            else ""
        )
        if branch_city.lower() == city.lower():
            return branch
    return None


def update_branch(branch_id, update_data):
    """Update branch information"""
    if DYNAMODB_AVAILABLE:
        try:
            table = get_table(BRANCHES_TABLE)
            if table:
                # Build update expression dynamically
                update_expr = "SET "
                expr_attrs = {}
                expr_names = {}

                for key, value in update_data.items():
                    if key != "branch_id":
                        update_expr += f"#{key} = :{key}, "
                        expr_names[f"#{key}"] = key
                        expr_attrs[f":{key}"] = value

                update_expr = update_expr.rstrip(", ")

                response = table.update_item(
                    Key={"branch_id": branch_id},
                    UpdateExpression=update_expr,
                    ExpressionAttributeNames=expr_names,
                    ExpressionAttributeValues=expr_attrs,
                )
                return response
        except Exception as e:
            print(f"Error updating branch in DynamoDB: {e}")

    # Fallback to mock database
    for branch in mock_branches:
        if branch.get("branch_id") == branch_id:
            branch.update(update_data)
            break
    return {"ResponseMetadata": {"HTTPStatusCode": 200}}


# Loyalty program operations (Cross-branch)
def get_loyalty_points(user_id):
    """Get user's loyalty points"""
    if DYNAMODB_AVAILABLE:
        try:
            table = get_table(LOYALTY_TABLE)
            if table:
                response = table.get_item(Key={"user_id": user_id})
                item = response.get("Item")
                if item:
                    return item.get("points", 0), item.get("tier", "Silver")
                return 0, "Silver"
        except Exception as e:
            print(f"Error getting loyalty points from DynamoDB: {e}")

    # Fallback to mock database
    for loyalty in mock_loyalty:
        if loyalty.get("user_id") == user_id:
            return loyalty.get("points", 0), loyalty.get("tier", "Silver")
    return 0, "Silver"


def add_loyalty_points(user_id, points, reason="booking"):
    """Add loyalty points to user account"""
    if DYNAMODB_AVAILABLE:
        try:
            table = get_table(LOYALTY_TABLE)
            if table:
                # Get current points
                current_points, current_tier = get_loyalty_points(user_id)
                new_points = current_points + points

                # Determine tier
                if new_points >= 20001:
                    tier = "Platinum"
                elif new_points >= 5001:
                    tier = "Gold"
                else:
                    tier = "Silver"

                # Update or create loyalty record
                table.put_item(
                    Item={
                        "user_id": user_id,
                        "points": new_points,
                        "tier": tier,
                        "last_updated": datetime.now().isoformat(),
                        "transactions": table.get_item(Key={"user_id": user_id})
                        .get("Item", {})
                        .get("transactions", [])
                        + [
                            {
                                "points": points,
                                "reason": reason,
                                "timestamp": datetime.now().isoformat(),
                            }
                        ],
                    }
                )
                return new_points, tier
        except Exception as e:
            print(f"Error adding loyalty points to DynamoDB: {e}")

    # Fallback to mock database
    current_points, current_tier = get_loyalty_points(user_id)
    new_points = current_points + points

    if new_points >= 20001:
        tier = "Platinum"
    elif new_points >= 5001:
        tier = "Gold"
    else:
        tier = "Silver"

    # Update or create in mock
    loyalty_found = False
    for loyalty in mock_loyalty:
        if loyalty.get("user_id") == user_id:
            loyalty["points"] = new_points
            loyalty["tier"] = tier
            loyalty["last_updated"] = datetime.now().isoformat()
            loyalty_found = True
            break

    if not loyalty_found:
        mock_loyalty.append(
            {
                "user_id": user_id,
                "points": new_points,
                "tier": tier,
                "last_updated": datetime.now().isoformat(),
                "transactions": [
                    {
                        "points": points,
                        "reason": reason,
                        "timestamp": datetime.now().isoformat(),
                    }
                ],
            }
        )

    return new_points, tier


def redeem_loyalty_points(user_id, points_to_redeem):
    """Redeem loyalty points"""
    current_points, tier = get_loyalty_points(user_id)

    if current_points < points_to_redeem:
        return False, current_points, tier

    new_points = current_points - points_to_redeem

    # Update tier if needed
    if new_points >= 20001:
        tier = "Platinum"
    elif new_points >= 5001:
        tier = "Gold"
    else:
        tier = "Silver"

    if DYNAMODB_AVAILABLE:
        try:
            table = get_table(LOYALTY_TABLE)
            if table:
                table.update_item(
                    Key={"user_id": user_id},
                    UpdateExpression="SET points = :p, tier = :t, last_updated = :u",
                    ExpressionAttributeValues={
                        ":p": new_points,
                        ":t": tier,
                        ":u": datetime.now().isoformat(),
                    },
                )
        except Exception as e:
            print(f"Error redeeming loyalty points in DynamoDB: {e}")

    # Update mock
    for loyalty in mock_loyalty:
        if loyalty.get("user_id") == user_id:
            loyalty["points"] = new_points
            loyalty["tier"] = tier
            loyalty["last_updated"] = datetime.now().isoformat()
            break

    return True, new_points, tier


# Initialize Indian branches
def init_indian_branches():
    """Initialize the 5 Indian branches for Blissful Abodes"""
    branches = [
        {
            "branch_id": "BLISS-MUM",
            "branch_name": "Blissful Abodes Mumbai",
            "location": {
                "address": "Bandra Kurla Complex, Mumbai",
                "city": "Mumbai",
                "state": "Maharashtra",
                "pincode": "400051",
                "latitude": 19.0542,
                "longitude": 72.8256,
            },
            "contact": {
                "phone": "+91-22-6123-4567",
                "email": "mumbai@blissfulabodes.com",
                "manager": "Rajesh Kumar",
            },
            "amenities": [
                "Pool",
                "Spa",
                "Restaurant",
                "Gym",
                "Sea-facing rooms",
                "Rooftop infinity pool",
                "Conference facilities",
            ],
            "check_in_time": "14:00",
            "check_out_time": "12:00",
            "total_rooms": 80,
            "room_types_available": ["single", "double", "family", "couple", "vip"],
            "starting_price": 4500,
            "status": "active",
            "created_at": datetime.now().isoformat(),
        },
        {
            "branch_id": "BLISS-DEL",
            "branch_name": "Blissful Abodes Delhi",
            "location": {
                "address": "Connaught Place, New Delhi",
                "city": "Delhi",
                "state": "Delhi",
                "pincode": "110001",
                "latitude": 28.6304,
                "longitude": 77.2177,
            },
            "contact": {
                "phone": "+91-11-4987-6543",
                "email": "delhi@blissfulabodes.com",
                "manager": "Priya Sharma",
            },
            "amenities": [
                "Heritage wing",
                "Business center",
                "Ayurvedic spa",
                "Fine dining restaurant",
            ],
            "check_in_time": "14:00",
            "check_out_time": "12:00",
            "total_rooms": 100,
            "room_types_available": ["single", "double", "family", "couple", "vip"],
            "starting_price": 5000,
            "status": "active",
            "created_at": datetime.now().isoformat(),
        },
        {
            "branch_id": "BLISS-BLR",
            "branch_name": "Blissful Abodes Bangalore",
            "location": {
                "address": "MG Road, Bangalore",
                "city": "Bangalore",
                "state": "Karnataka",
                "pincode": "560001",
                "latitude": 12.9716,
                "longitude": 77.5946,
            },
            "contact": {
                "phone": "+91-80-2345-6789",
                "email": "bangalore@blissfulabodes.com",
                "manager": "Arjun Reddy",
            },
            "amenities": [
                "Tech-friendly rooms",
                "Startup lounge",
                "EV charging stations",
                "Tech support 24/7",
            ],
            "check_in_time": "14:00",
            "check_out_time": "12:00",
            "total_rooms": 70,
            "room_types_available": ["single", "double", "family", "couple", "vip"],
            "starting_price": 4800,
            "status": "active",
            "created_at": datetime.now().isoformat(),
        },
        {
            "branch_id": "BLISS-GOA",
            "branch_name": "Blissful Abodes Goa",
            "location": {
                "address": "Calangute Beach, Goa",
                "city": "Goa",
                "state": "Goa",
                "pincode": "403516",
                "latitude": 15.5439,
                "longitude": 73.7553,
            },
            "contact": {
                "phone": "+91-832-245-6789",
                "email": "goa@blissfulabodes.com",
                "manager": "Maria Fernandes",
            },
            "amenities": [
                "Beach access",
                "Watersports center",
                "Pool villas",
                "Yoga studio",
            ],
            "check_in_time": "14:00",
            "check_out_time": "12:00",
            "total_rooms": 60,
            "room_types_available": ["single", "double", "family", "couple", "vip"],
            "starting_price": 6000,
            "status": "active",
            "created_at": datetime.now().isoformat(),
        },
        {
            "branch_id": "BLISS-CHE",
            "branch_name": "Blissful Abodes Chennai",
            "location": {
                "address": "Marina Beach Road, Chennai",
                "city": "Chennai",
                "state": "Tamil Nadu",
                "pincode": "600006",
                "latitude": 13.0827,
                "longitude": 80.2707,
            },
            "contact": {
                "phone": "+91-44-4567-8901",
                "email": "chennai@blissfulabodes.com",
                "manager": "Rajesh Krishnan",
            },
            "amenities": [
                "Beach view rooms",
                "Traditional South Indian restaurant",
                "Ayurvedic spa",
                "Cultural temple tours",
            ],
            "check_in_time": "14:00",
            "check_out_time": "12:00",
            "total_rooms": 100,
            "room_types_available": ["single", "double", "family", "couple", "vip"],
            "starting_price": 4500,
            "status": "active",
            "created_at": datetime.now().isoformat(),
        },
    ]

    # Add branches if they don't exist
    for branch in branches:
        existing = get_branch(branch["branch_id"])
        if not existing:
            add_branch(branch)
            print(f"Initialized branch: {branch['branch_name']}")

    return branches


# Favorites Management
def add_favorite_room(user_id, room_id):
    """Add a room to user's favorites"""
    favorite_data = {
        "user_id": user_id,
        "room_id": room_id,
        "added_at": datetime.now().isoformat(),
    }

    # Check if already favorited
    for fav in mock_favorites:
        if fav.get("user_id") == user_id and fav.get("room_id") == room_id:
            return {
                "ResponseMetadata": {"HTTPStatusCode": 200},
                "message": "Already favorited",
            }

    mock_favorites.append(favorite_data)
    return {
        "ResponseMetadata": {"HTTPStatusCode": 200},
        "message": "Added to favorites",
    }


def remove_favorite_room(user_id, room_id):
    """Remove a room from user's favorites"""
    global mock_favorites
    initial_count = len(mock_favorites)
    mock_favorites = [
        f
        for f in mock_favorites
        if not (f.get("user_id") == user_id and f.get("room_id") == room_id)
    ]

    if len(mock_favorites) < initial_count:
        return {
            "ResponseMetadata": {"HTTPStatusCode": 200},
            "message": "Removed from favorites",
        }
    return {
        "ResponseMetadata": {"HTTPStatusCode": 404},
        "message": "Favorite not found",
    }


def get_user_favorites(user_id):
    """Get all favorite rooms for a user"""
    favorite_room_ids = [
        f.get("room_id") for f in mock_favorites if f.get("user_id") == user_id
    ]

    # Get full room details for each favorite
    favorite_rooms = []
    for room_id in favorite_room_ids:
        room = get_room(room_id)
        if room:
            favorite_rooms.append(room)

    return favorite_rooms


def is_room_favorited(user_id, room_id):
    """Check if a room is favorited by user"""
    for fav in mock_favorites:
        if fav.get("user_id") == user_id and fav.get("room_id") == room_id:
            return True
    return False


# Enhanced Booking Functions
def get_past_bookings(user_id):
    """Get past bookings for a user (completed or cancelled)"""
    all_bookings = get_user_bookings(user_id)
    today = datetime.now().date()

    past_bookings = []
    for booking in all_bookings:
        booking = normalize_booking(booking)
        try:
            check_out_str = booking.get("check_out", "")
            if check_out_str:
                check_out = datetime.strptime(check_out_str, "%Y-%m-%d").date()
                if check_out < today or booking.get("status") in [
                    "completed",
                    "cancelled",
                ]:
                    past_bookings.append(booking)
            elif booking.get("status") in ["completed", "cancelled"]:
                # Include if status is completed/cancelled even without date
                past_bookings.append(booking)
        except (ValueError, TypeError, AttributeError) as e:
            # Try alternate date format if YYYY-MM-DD fails
            try:
                if check_out_str:
                    check_out = datetime.strptime(check_out_str, "%d/%m/%Y").date()
                    if check_out < today or booking.get("status") in [
                        "completed",
                        "cancelled",
                    ]:
                        past_bookings.append(booking)
            except Exception:
                print(f"Error parsing past booking date '{check_out_str}': {e}")
                pass

    return sorted(past_bookings, key=lambda x: x.get("check_out", ""), reverse=True)


def get_upcoming_bookings(user_id):
    """Get upcoming bookings for a user"""
    all_bookings = get_user_bookings(user_id)
    today = datetime.now().date()

    upcoming_bookings = []
    for booking in all_bookings:
        booking = normalize_booking(booking)
        try:
            check_in_str = booking.get("check_in", "")
            if check_in_str:
                check_in = datetime.strptime(check_in_str, "%Y-%m-%d").date()
                if check_in >= today and booking.get("status") == "confirmed":
                    upcoming_bookings.append(booking)
        except (ValueError, TypeError, AttributeError) as e:
            # Try alternate date format if YYYY-MM-DD fails
            try:
                if check_in_str:
                    check_in = datetime.strptime(check_in_str, "%d/%m/%Y").date()
                    if check_in >= today and booking.get("status") == "confirmed":
                        upcoming_bookings.append(booking)
            except Exception:
                print(f"Error parsing upcoming booking date '{check_in_str}': {e}")
                pass

    return sorted(upcoming_bookings, key=lambda x: x.get("check_in", ""))


def calculate_total_spent(user_id):
    """Calculate total amount spent by user on completed bookings"""
    all_bookings = get_user_bookings(user_id)
    total = 0

    for booking in all_bookings:
        booking = normalize_booking(booking)
        if booking.get("status") in ["confirmed", "completed"]:
            try:
                # Handle both attribute and dict access
                price = booking.get("total_price", 0) or booking.get("price", 0)
                if price:
                    total += float(price)
            except (ValueError, TypeError, AttributeError) as e:
                print(f"Error calculating price for booking: {e}")
                pass

    return round(total, 2)


def get_booking_stats(user_id):
    """Get comprehensive booking statistics for a user"""
    all_bookings = get_user_bookings(user_id)
    today = datetime.now().date()

    stats = {
        "total_bookings": len(all_bookings),
        "upcoming": 0,
        "past": 0,
        "completed": 0,
        "cancelled": 0,
        "total_spent": 0,
        "total_nights": 0,
    }

    for booking in all_bookings:
        booking = normalize_booking(booking)
        status = booking.get("status", "")

        # Count by status
        if status == "cancelled":
            stats["cancelled"] += 1
        elif status == "completed":
            stats["completed"] += 1

        # Calculate spent
        if status in ["confirmed", "completed"]:
            try:
                # Handle both attribute and dict access
                price = booking.get("total_price", 0) or booking.get("price", 0)
                if price:
                    stats["total_spent"] += float(price)
            except (ValueError, TypeError, AttributeError) as e:
                print(f"Error calculating price for booking: {e}")
                pass

        # Count upcoming vs past
        try:
            check_in_str = booking.get("check_in", "")
            check_out_str = booking.get("check_out", "")

            if check_in_str and check_out_str:
                check_in = datetime.strptime(check_in_str, "%Y-%m-%d").date()
                check_out = datetime.strptime(check_out_str, "%Y-%m-%d").date()

                if check_out < today:
                    stats["past"] += 1
                elif check_in >= today and status == "confirmed":
                    stats["upcoming"] += 1

                # Calculate nights
                nights = (check_out - check_in).days
                stats["total_nights"] += nights
        except (ValueError, TypeError, AttributeError) as e:
            print(f"Error parsing dates for booking: {e}")
            pass

    stats["total_spent"] = round(stats["total_spent"], 2)
    return stats


def normalize_booking(booking):
    """Ensure booking has all required fields with proper defaults"""
    if not booking:
        return booking

    # Ensure total_price exists
    if "total_price" not in booking:
        booking["total_price"] = booking.get("price", 0)

    # Ensure status exists
    if "status" not in booking:
        booking["status"] = "pending"

    # Ensure dates exist
    if "check_in" not in booking:
        booking["check_in"] = ""
    if "check_out" not in booking:
        booking["check_out"] = ""

    # Ensure booking_id exists
    if "booking_id" not in booking:
        booking["booking_id"] = booking.get("id", str(uuid.uuid4()))

    # Ensure room info exists
    if "room_id" not in booking:
        booking["room_id"] = ""
    if "room_name" not in booking:
        booking["room_name"] = ""

    return booking


# Debug: Print data on module load
print(f"\n=== DATABASE INITIALIZATION ===")
print(f"Mock Users: {len(mock_users)}")
print(f"Mock Rooms: {len(mock_rooms)}")
print(f"Mock Bookings: {len(mock_bookings)}")
print(f"Mock Reviews: {len(mock_reviews)}")
print(f"Mock Branches: {len(mock_branches)}")
print(f"===============================\n")


def get_room_image_url(room_type=None, room_index=0):
    """
    Get a unique room image URL from local static images.
    Returns different images for different room types to show variety.
    """
    # Collection of local room images from static/images folder
    room_image_collection = {
        "single": [
            "/static/images/1bed1.jpeg",
            "/static/images/1bed2.jpeg",
            "/static/images/1bed3.jpeg",
            "/static/images/1bed4.jpeg",
            "/static/images/1bed5.jpeg",
            "/static/images/1bed7.jpg",
            "/static/images/1bed8.jpg",
        ],
        "double": [
            "/static/images/2bed1.jpeg",
            "/static/images/2bed2.jpeg",
            "/static/images/2bed3.jpeg",
            "/static/images/2bed4.jpeg",
            "/static/images/2bed5.jpeg",
            "/static/images/2bed6.jpg",
            "/static/images/2bed7.jpg",
            "/static/images/2bed8.jpg",
        ],
        "family": [
            "/static/images/family1.jpeg",
            "/static/images/family2.jpeg",
            "/static/images/family3.jpeg",
            "/static/images/family4.jpeg",
            "/static/images/family6.jpg",
            "/static/images/2bed5.jpeg",
        ],
        "couple": [
            "/static/images/couple1.jpeg",
            "/static/images/couple2.jpeg",
            "/static/images/couple3.jpeg",
            "/static/images/couple4.jpeg",
            "/static/images/couple5.jpeg",
            "/static/images/couple6.jpg",
        ],
        "vip": [
            "/static/images/vip1.jpeg",
            "/static/images/vip2.jpeg",
            "/static/images/vip3.jpeg",
            "/static/images/vip4.jpeg",
            "/static/images/vip5.jpeg",
            "/static/images/vip6.jpg",
            "/static/images/vip7.jpg",
            "/static/images/vip8.jpg",
        ],
        "default": [
            "/static/images/1bed1.jpeg",
            "/static/images/2bed1.jpeg",
            "/static/images/vip1.jpeg",
        ],
    }

    if not room_type:
        room_type = "default"

    room_type_lower = str(room_type).lower()
    if "single" in room_type_lower or room_type_lower == "1":
        category = "single"
    elif "double" in room_type_lower or room_type_lower == "2":
        category = "double"
    elif "family" in room_type_lower or "suite" in room_type_lower:
        category = "family"
    elif (
        "couple" in room_type_lower
        or "romantic" in room_type_lower
        or "honeymoon" in room_type_lower
    ):
        category = "couple"
    elif (
        "vip" in room_type_lower
        or "presidential" in room_type_lower
        or "executive" in room_type_lower
    ):
        category = "vip"
    else:
        category = "default"

    images = room_image_collection.get(category, room_image_collection["default"])
    selected_image = images[room_index % len(images)]

    return selected_image


def populate_rooms_with_images():
    """Populate database with 100+ sample rooms with images"""

    if len(mock_rooms) > 10:
        return

    # Get all branches
    branches = get_all_branches(status="active")
    branch_ids = [b.get("branch_id") for b in branches if b.get("branch_id")]

    # Indian cities with branch mapping
    cities = [
        ("Mumbai, Maharashtra", "BLISS-MUM"),
        ("New Delhi, Delhi", "BLISS-DEL"),
        ("Bangalore, Karnataka", "BLISS-BLR"),
        ("Goa", "BLISS-GOA"),
        ("Chennai, Tamil Nadu", "BLISS-CHE"),
    ]

    room_count = 0

    # Single Rooms (30)
    for i in range(1, 31):
        city_info = cities[i % len(cities)]
        city_name = city_info[0] if isinstance(city_info, tuple) else city_info
        branch_id = city_info[1] if isinstance(city_info, tuple) else None
        if not branch_id and branch_ids:
            branch_id = branch_ids[i % len(branch_ids)]

        room = {
            "room_id": str(uuid.uuid4()),
            "name": f"Single Room {i:03d}",
            "room_type": "single",
            "location": city_name,
            "branch_id": branch_id,
            "price": 3999 + ((i - 1) % 6) * 1000,
            "capacity": 1,
            "amenities": ["WiFi", "TV", "AC", "Work Desk", "Private Bathroom"],
            "availability": "available" if i % 10 != 0 else "unavailable",
            "image": get_room_image_url("single", i - 1),
            "vr_enabled": True,
            "created_at": datetime.now().isoformat(),
        }
        add_room(room)
        room_count += 1

    # Double Rooms (30)
    for i in range(1, 31):
        city_info = cities[(i + 1) % len(cities)]
        city_name = city_info[0] if isinstance(city_info, tuple) else city_info
        branch_id = city_info[1] if isinstance(city_info, tuple) else None
        if not branch_id and branch_ids:
            branch_id = branch_ids[(i + 1) % len(branch_ids)]

        room = {
            "room_id": str(uuid.uuid4()),
            "name": f"Double Room {i:03d}",
            "room_type": "double",
            "location": city_name,
            "branch_id": branch_id,
            "price": 5999 + ((i - 1) % 10) * 1000,
            "capacity": 2,
            "amenities": [
                "Double Bed",
                "WiFi",
                "TV",
                "AC",
                "Mini Fridge",
                "Private Bathroom",
                "Coffee Maker",
            ],
            "availability": "available" if i % 8 != 0 else "unavailable",
            "image": get_room_image_url("double", i - 1),
            "vr_enabled": True,
            "created_at": datetime.now().isoformat(),
        }
        add_room(room)
        room_count += 1

    # Family Rooms (20)
    for i in range(1, 21):
        beds = 3 + (i % 3)
        city_info = cities[(i + 2) % len(cities)]
        city_name = city_info[0] if isinstance(city_info, tuple) else city_info
        branch_id = city_info[1] if isinstance(city_info, tuple) else None
        if not branch_id and branch_ids:
            branch_id = branch_ids[(i + 2) % len(branch_ids)]

        room = {
            "room_id": str(uuid.uuid4()),
            "name": f"Family Suite {i:03d} ({beds} Beds)",
            "room_type": "family",
            "location": city_name,
            "branch_id": branch_id,
            "price": 8999 + ((i - 1) % 10) * 1500 + (beds * 1000),
            "capacity": 2 * beds,
            "amenities": [
                f"{beds} Queen Beds",
                "WiFi",
                "Multiple TVs",
                "AC",
                "Kitchenette",
                "Two Bathrooms",
                "Sofa Bed",
                "Dining Area",
            ],
            "availability": "available" if i % 7 != 0 else "unavailable",
            "image": get_room_image_url("family", i - 1),
            "vr_enabled": True,
            "created_at": datetime.now().isoformat(),
        }
        add_room(room)
        room_count += 1

    # Couple/Romantic Rooms (10)
    romantic_names = [
        "Honeymoon Suite",
        "Romantic Retreat",
        "Lovers Paradise",
        "Intimate Escape",
        "Romance Suite",
        "Passion Palace",
    ]
    for i in range(1, 11):
        city_info = cities[(i + 3) % len(cities)]
        city_name = city_info[0] if isinstance(city_info, tuple) else city_info
        branch_id = city_info[1] if isinstance(city_info, tuple) else None
        if not branch_id and branch_ids:
            branch_id = branch_ids[(i + 3) % len(branch_ids)]

        room = {
            "room_id": str(uuid.uuid4()),
            "name": f"{romantic_names[i % len(romantic_names)]} {i:02d}",
            "room_type": "couple",
            "location": city_name,
            "branch_id": branch_id,
            "price": 12999 + ((i - 1) % 8) * 2000,
            "capacity": 2,
            "amenities": [
                "King Bed",
                "WiFi",
                "Smart TV",
                "AC",
                "Jacuzzi",
                "Champagne Bucket",
                "Romantic Decor",
                "Balcony",
                "Premium Toiletries",
            ],
            "availability": "available" if i % 6 != 0 else "unavailable",
            "image": get_room_image_url("couple", i - 1),
            "vr_enabled": True,
            "created_at": datetime.now().isoformat(),
        }
        add_room(room)
        room_count += 1

    # VIP/Presidential Suites (10)
    vip_names = [
        "Presidential Suite",
        "Executive Penthouse",
        "Royal Chamber",
        "Celebrity Suite",
        "Platinum Residence",
        "Diamond Palace",
        "Elite Retreat",
        "Signature Villa",
        "Luxury Mansion",
        "Grand Suite",
    ]
    for i in range(1, 11):
        city_info = cities[(i + 4) % len(cities)]
        city_name = city_info[0] if isinstance(city_info, tuple) else city_info
        branch_id = city_info[1] if isinstance(city_info, tuple) else None
        if not branch_id and branch_ids:
            branch_id = branch_ids[(i + 4) % len(branch_ids)]

        room = {
            "room_id": str(uuid.uuid4()),
            "name": f"{vip_names[i-1]} {i:02d}",
            "room_type": "vip",
            "location": city_name,
            "branch_id": branch_id,
            "price": 39999 + ((i - 1) % 10) * 7000,
            "capacity": 4 + (i % 3),
            "amenities": [
                "Multiple King Beds",
                "High-speed WiFi",
                "Multiple Smart TVs",
                "Smart Home System",
                "Private Jacuzzi",
                "Wet Bar",
                "Full Kitchen",
                "Dining Room",
                "Living Area",
                "Premium Sound System",
                "Butler Service",
                "Panoramic Views",
            ],
            "availability": "available" if i % 5 != 0 else "unavailable",
            "image": get_room_image_url("vip", i - 1),
            "vr_enabled": True,
            "created_at": datetime.now().isoformat(),
        }
        add_room(room)
        room_count += 1


# ============================================================================
# CHATBOT FUNCTIONS
# ============================================================================


def add_chat_message(user_id, message, sender="user", message_type="text"):
    """Add a chat message"""
    if not DYNAMODB_AVAILABLE:
        message_data = {
            "message_id": str(uuid.uuid4()),
            "user_id": user_id,
            "message": message,
            "sender": sender,  # 'user', 'bot', 'admin', 'staff'
            "message_type": message_type,  # 'text', 'booking', 'review', 'report', 'extra_service'
            "timestamp": datetime.now().isoformat(),
            "read": False,
        }
        mock_chat_messages.append(message_data)
        return message_data

    try:
        table = dynamodb.Table(CHAT_MESSAGES_TABLE)
        message_id = str(uuid.uuid4())
        message_data = {
            "message_id": message_id,
            "user_id": user_id,
            "message": message,
            "sender": sender,
            "message_type": message_type,
            "timestamp": datetime.now().isoformat(),
            "read": False,
        }
        table.put_item(Item=message_data)
        return message_data
    except Exception as e:
        print(f"Error adding chat message: {e}")
        return None


def get_user_chat_messages(user_id, limit=50):
    """Get chat messages for a user"""
    if not DYNAMODB_AVAILABLE:
        user_messages = [msg for msg in mock_chat_messages if msg["user_id"] == user_id]
        return sorted(user_messages, key=lambda x: x["timestamp"], reverse=True)[:limit]

    try:
        table = dynamodb.Table(CHAT_MESSAGES_TABLE)
        response = table.query(
            IndexName="UserMessagesIndex",
            KeyConditionExpression=Key("user_id").eq(user_id),
            ScanIndexForward=False,
            Limit=limit,
        )
        return response.get("Items", [])
    except Exception as e:
        print(f"Error getting chat messages: {e}")
        return []


def mark_messages_as_read(user_id):
    """Mark all messages as read for a user"""
    if not DYNAMODB_AVAILABLE:
        for msg in mock_chat_messages:
            if msg["user_id"] == user_id:
                msg["read"] = True
        return True

    try:
        messages = get_user_chat_messages(user_id)
        table = dynamodb.Table(CHAT_MESSAGES_TABLE)
        for msg in messages:
            if not msg.get("read", False):
                table.update_item(
                    Key={"message_id": msg["message_id"]},
                    UpdateExpression="SET #read = :read",
                    ExpressionAttributeNames={"#read": "read"},
                    ExpressionAttributeValues={":read": True},
                )
        return True
    except Exception as e:
        print(f"Error marking messages as read: {e}")
        return False


def add_chat_request(user_id, request_type, details, branch_id=None):
    """Add a chat request (booking, review, report, extra_service)"""
    if not DYNAMODB_AVAILABLE:
        request_data = {
            "request_id": str(uuid.uuid4()),
            "user_id": user_id,
            "request_type": request_type,  # 'booking', 'review', 'report', 'extra_service'
            "details": details,
            "status": "pending",  # 'pending', 'processing', 'completed', 'cancelled'
            "branch_id": branch_id,
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat(),
            "admin_notes": "",
            "staff_assigned": None,
        }
        mock_chat_requests.append(request_data)
        return request_data

    try:
        table = dynamodb.Table(CHAT_REQUESTS_TABLE)
        request_id = str(uuid.uuid4())
        request_data = {
            "request_id": request_id,
            "user_id": user_id,
            "request_type": request_type,
            "details": details,
            "status": "pending",
            "branch_id": branch_id,
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat(),
            "admin_notes": "",
            "staff_assigned": None,
        }
        table.put_item(Item=request_data)
        return request_data
    except Exception as e:
        print(f"Error adding chat request: {e}")
        return None


def get_chat_requests(status=None, request_type=None, user_id=None):
    """Get chat requests with optional filters"""
    if not DYNAMODB_AVAILABLE:
        requests = mock_chat_requests
        if user_id:
            requests = [r for r in requests if r["user_id"] == user_id]
        if status:
            requests = [r for r in requests if r["status"] == status]
        if request_type:
            requests = [r for r in requests if r["request_type"] == request_type]
        return sorted(requests, key=lambda x: x["created_at"], reverse=True)

    try:
        table = dynamodb.Table(CHAT_REQUESTS_TABLE)

        if user_id:
            response = table.query(
                IndexName="UserRequestsIndex",
                KeyConditionExpression=Key("user_id").eq(user_id),
            )
        elif status and request_type:
            response = table.query(
                IndexName="StatusTypeIndex",
                KeyConditionExpression=Key("status").eq(status)
                & Key("request_type").eq(request_type),
            )
        elif status:
            response = table.query(
                IndexName="StatusTypeIndex",
                KeyConditionExpression=Key("status").eq(status),
            )
        else:
            response = table.scan()

        return response.get("Items", [])
    except Exception as e:
        print(f"Error getting chat requests: {e}")
        return []


def update_chat_request(request_id, status=None, admin_notes=None, staff_assigned=None):
    """Update a chat request"""
    if not DYNAMODB_AVAILABLE:
        for req in mock_chat_requests:
            if req["request_id"] == request_id:
                if status:
                    req["status"] = status
                if admin_notes:
                    req["admin_notes"] = admin_notes
                if staff_assigned:
                    req["staff_assigned"] = staff_assigned
                req["updated_at"] = datetime.now().isoformat()
                return req
        return None

    try:
        table = dynamodb.Table(CHAT_REQUESTS_TABLE)
        update_expr = "SET updated_at = :updated"
        expr_values = {":updated": datetime.now().isoformat()}
        expr_names = {}

        if status:
            update_expr += ", #status = :status"
            expr_values[":status"] = status
            expr_names["#status"] = "status"
        if admin_notes:
            update_expr += ", admin_notes = :notes"
            expr_values[":notes"] = admin_notes
        if staff_assigned:
            update_expr += ", staff_assigned = :staff"
            expr_values[":staff"] = staff_assigned

        kwargs = {
            "Key": {"request_id": request_id},
            "UpdateExpression": update_expr,
            "ExpressionAttributeValues": expr_values,
            "ReturnValues": "ALL_NEW",
        }

        if expr_names:
            kwargs["ExpressionAttributeNames"] = expr_names

        response = table.update_item(**kwargs)
        return response.get("Attributes")
    except Exception as e:
        print(f"Error updating chat request: {e}")
        return None


def get_chat_request(request_id):
    """Get a specific chat request"""
    if not DYNAMODB_AVAILABLE:
        for req in mock_chat_requests:
            if req["request_id"] == request_id:
                return req
        return None

    try:
        table = dynamodb.Table(CHAT_REQUESTS_TABLE)
        response = table.get_item(Key={"request_id": request_id})
        return response.get("Item")
    except Exception as e:
        print(f"Error getting chat request: {e}")
        return None


def get_unread_messages_count(user_id):
    """Get count of unread messages for a user"""
    if not DYNAMODB_AVAILABLE:
        return len(
            [
                msg
                for msg in mock_chat_messages
                if msg["user_id"] == user_id and not msg.get("read", False)
            ]
        )

    try:
        messages = get_user_chat_messages(user_id)
        return len([msg for msg in messages if not msg.get("read", False)])
    except Exception as e:
        print(f"Error getting unread messages count: {e}")
        return 0


def get_all_chat_messages(limit=100):
    """Get all chat messages for admin"""
    if not DYNAMODB_AVAILABLE:
        return sorted(mock_chat_messages, key=lambda x: x["timestamp"], reverse=True)[
            :limit
        ]

    try:
        table = dynamodb.Table(CHAT_MESSAGES_TABLE)
        response = table.scan(Limit=limit)
        items = response.get("Items", [])
        return sorted(items, key=lambda x: x["timestamp"], reverse=True)
    except Exception as e:
        print(f"Error getting all chat messages: {e}")
        return []


def delete_chat_message(message_id):
    """Delete a chat message"""
    if not DYNAMODB_AVAILABLE:
        global mock_chat_messages
        mock_chat_messages = [
            msg for msg in mock_chat_messages if msg["message_id"] != message_id
        ]
        return True

    try:
        table = dynamodb.Table(CHAT_MESSAGES_TABLE)
        table.delete_item(Key={"message_id": message_id})
        return True
    except Exception as e:
        print(f"Error deleting chat message: {e}")
        return False


def delete_chat_request(request_id):
    """Delete a chat request"""
    if not DYNAMODB_AVAILABLE:
        global mock_chat_requests
        mock_chat_requests = [
            req for req in mock_chat_requests if req["request_id"] != request_id
        ]
        return True

    try:
        table = dynamodb.Table(CHAT_REQUESTS_TABLE)
        table.delete_item(Key={"request_id": request_id})
        return True
    except Exception as e:
        print(f"Error deleting chat request: {e}")
        return False


# ============================================================================
# DYNAMIC PRICING ENGINE
# ============================================================================


def add_pricing_rule(rule_data):
    """Add a dynamic pricing rule"""
    if not DYNAMODB_AVAILABLE:
        mock_pricing_rules.append(rule_data)
        return True

    try:
        table = dynamodb.Table(PRICING_RULES_TABLE)
        table.put_item(Item=rule_data)
        return True
    except Exception as e:
        print(f"Error adding pricing rule: {e}")
        return False


def get_pricing_rules(branch_id=None, rule_type=None):
    """Get pricing rules, optionally filtered by branch or type"""
    if not DYNAMODB_AVAILABLE:
        rules = mock_pricing_rules
        if branch_id:
            rules = [
                r
                for r in rules
                if r.get("branch_id") == branch_id or r.get("branch_id") == "all"
            ]
        if rule_type:
            rules = [r for r in rules if r.get("rule_type") == rule_type]
        return rules

    try:
        table = dynamodb.Table(PRICING_RULES_TABLE)
        if branch_id:
            try:
                response = table.query(
                    IndexName="BranchRulesIndex",
                    KeyConditionExpression=Key("branch_id").eq(branch_id),
                )
                rules = response.get("Items", [])
            except Exception as e:
                # Fallback to scan if index is missing
                if "ValidationException" in str(
                    e
                ) or "The table does not have the specified index" in str(e):
                    print(
                        "DEBUG: BranchRulesIndex missing, falling back to SCAN for pricing rules"
                    )
                    response = table.scan(
                        FilterExpression=Attr("branch_id").eq(branch_id)
                    )
                    rules = response.get("Items", [])
                else:
                    raise e
        else:
            response = table.scan()
            rules = response.get("Items", [])

        if rule_type:
            rules = [r for r in rules if r.get("rule_type") == rule_type]
        return rules
    except Exception as e:
        print(f"Error getting pricing rules: {e}")
        return []


def calculate_dynamic_price(
    base_price, check_in_date, check_out_date, room_id, branch_id
):
    """Calculate dynamic price based on pricing rules"""
    try:
        check_in = (
            datetime.strptime(check_in_date, "%Y-%m-%d")
            if isinstance(check_in_date, str)
            else check_in_date
        )
        check_out = (
            datetime.strptime(check_out_date, "%Y-%m-%d")
            if isinstance(check_out_date, str)
            else check_out_date
        )
        nights = (check_out - check_in).days

        if nights <= 0:
            return base_price

        total_price = 0
        rules = get_pricing_rules(branch_id)

        # Calculate price for each night
        current_date = check_in
        while current_date < check_out:
            night_price = base_price
            multiplier = 1.0

            for rule in rules:
                if not rule.get("active", True):
                    continue

                rule_type = rule.get("rule_type")

                # Weekend pricing
                if rule_type == "weekend" and current_date.weekday() in [
                    4,
                    5,
                ]:  # Friday, Saturday
                    multiplier *= rule.get("multiplier", 1.0)

                # Weekday pricing
                elif rule_type == "weekday" and current_date.weekday() not in [4, 5, 6]:
                    multiplier *= rule.get("multiplier", 1.0)

                # Peak season
                elif rule_type == "peak_season":
                    start_date = datetime.strptime(rule.get("start_date"), "%Y-%m-%d")
                    end_date = datetime.strptime(rule.get("end_date"), "%Y-%m-%d")
                    if start_date <= current_date <= end_date:
                        multiplier *= rule.get("multiplier", 1.0)

                # Last minute deals (within 3 days)
                elif rule_type == "last_minute":
                    days_until_checkin = (check_in - datetime.now()).days
                    if days_until_checkin <= rule.get("days_threshold", 3):
                        multiplier *= rule.get("multiplier", 1.0)

                # Early bird (more than 30 days in advance)
                elif rule_type == "early_bird":
                    days_until_checkin = (check_in - datetime.now()).days
                    if days_until_checkin >= rule.get("days_threshold", 30):
                        multiplier *= rule.get("multiplier", 1.0)

            night_price *= multiplier
            total_price += night_price
            current_date += timedelta(days=1)

        # Length of stay discount
        if nights >= 7:
            for rule in rules:
                if rule.get("rule_type") == "length_of_stay" and rule.get(
                    "active", True
                ):
                    min_nights = rule.get("min_nights", 7)
                    if nights >= min_nights:
                        discount = rule.get("discount_percent", 0) / 100
                        total_price *= 1 - discount
                        break

        return round(total_price, 2)

    except Exception as e:
        print(f"Error calculating dynamic price: {e}")
        return base_price * nights if nights > 0 else base_price


def init_default_pricing_rules(branch_id="all"):
    """Initialize default pricing rules"""
    default_rules = [
        {
            "rule_id": str(uuid.uuid4()),
            "branch_id": branch_id,
            "rule_type": "weekend",
            "name": "Weekend Premium",
            "multiplier": 1.3,  # 30% increase
            "active": True,
            "created_at": datetime.now().isoformat(),
        },
        {
            "rule_id": str(uuid.uuid4()),
            "branch_id": branch_id,
            "rule_type": "peak_season",
            "name": "Holiday Season",
            "start_date": "2024-12-20",
            "end_date": "2025-01-05",
            "multiplier": 1.5,  # 50% increase
            "active": True,
            "created_at": datetime.now().isoformat(),
        },
        {
            "rule_id": str(uuid.uuid4()),
            "branch_id": branch_id,
            "rule_type": "early_bird",
            "name": "Early Bird Discount",
            "days_threshold": 30,
            "multiplier": 0.9,  # 10% discount
            "active": True,
            "created_at": datetime.now().isoformat(),
        },
        {
            "rule_id": str(uuid.uuid4()),
            "branch_id": branch_id,
            "rule_type": "last_minute",
            "name": "Last Minute Deal",
            "days_threshold": 3,
            "multiplier": 0.85,  # 15% discount
            "active": True,
            "created_at": datetime.now().isoformat(),
        },
        {
            "rule_id": str(uuid.uuid4()),
            "branch_id": branch_id,
            "rule_type": "length_of_stay",
            "name": "Weekly Stay Discount",
            "min_nights": 7,
            "discount_percent": 10,
            "active": True,
            "created_at": datetime.now().isoformat(),
        },
    ]

    for rule in default_rules:
        add_pricing_rule(rule)

    return len(default_rules)


# ============================================================================
# GUEST PREFERENCES & HISTORY
# ============================================================================


def save_guest_preferences(user_id, preferences):
    """Save or update guest preferences"""
    if not DYNAMODB_AVAILABLE:
        # Update or add to mock
        for i, pref in enumerate(mock_guest_preferences):
            if pref.get("user_id") == user_id:
                mock_guest_preferences[i] = {
                    "user_id": user_id,
                    **preferences,
                    "updated_at": datetime.now().isoformat(),
                }
                return True

        mock_guest_preferences.append(
            {
                "user_id": user_id,
                **preferences,
                "created_at": datetime.now().isoformat(),
            }
        )
        return True

    try:
        table = dynamodb.Table(GUEST_PREFERENCES_TABLE)
        table.put_item(
            Item={
                "user_id": user_id,
                **preferences,
                "updated_at": datetime.now().isoformat(),
            }
        )
        return True
    except Exception as e:
        print(f"Error saving guest preferences: {e}")
        return False


def get_guest_preferences(user_id):
    """Get guest preferences"""
    if not DYNAMODB_AVAILABLE:
        for pref in mock_guest_preferences:
            if pref.get("user_id") == user_id:
                return pref
        return {}

    try:
        table = dynamodb.Table(GUEST_PREFERENCES_TABLE)
        response = table.get_item(Key={"user_id": user_id})
        return response.get("Item", {})
    except Exception as e:
        print(f"Error getting guest preferences: {e}")
        return {}


# ============================================================================
# WAITLIST SYSTEM
# ============================================================================


def add_to_waitlist(waitlist_data):
    """Add user to waitlist for a room"""
    if not DYNAMODB_AVAILABLE:
        mock_waitlist.append(waitlist_data)
        return True

    try:
        table = dynamodb.Table(WAITLIST_TABLE)
        table.put_item(Item=waitlist_data)
        return True
    except Exception as e:
        print(f"Error adding to waitlist: {e}")
        return False


def get_user_waitlist(user_id):
    """Get user's waitlist entries"""
    if not DYNAMODB_AVAILABLE:
        return [w for w in mock_waitlist if w.get("user_id") == user_id]

    try:
        table = dynamodb.Table(WAITLIST_TABLE)
        response = table.query(
            IndexName="UserWaitlistIndex",
            KeyConditionExpression=Key("user_id").eq(user_id),
        )
        return response.get("Items", [])
    except Exception as e:
        print(f"Error getting user waitlist: {e}")
        return []


def get_room_waitlist(room_id):
    """Get waitlist for a specific room"""
    if not DYNAMODB_AVAILABLE:
        return [
            w
            for w in mock_waitlist
            if w.get("room_id") == room_id and w.get("status") == "active"
        ]

    try:
        table = dynamodb.Table(WAITLIST_TABLE)
        response = table.query(
            IndexName="RoomWaitlistIndex",
            KeyConditionExpression=Key("room_id").eq(room_id),
        )
        waitlist = response.get("Items", [])
        return [w for w in waitlist if w.get("status") == "active"]
    except Exception as e:
        print(f"Error getting room waitlist: {e}")
        return []


def update_waitlist_status(waitlist_id, status):
    """Update waitlist entry status"""
    if not DYNAMODB_AVAILABLE:
        for w in mock_waitlist:
            if w.get("waitlist_id") == waitlist_id:
                w["status"] = status
                w["updated_at"] = datetime.now().isoformat()
                return True
        return False

    try:
        table = dynamodb.Table(WAITLIST_TABLE)
        table.update_item(
            Key={"waitlist_id": waitlist_id},
            UpdateExpression="SET #status = :status, updated_at = :updated",
            ExpressionAttributeNames={"#status": "status"},
            ExpressionAttributeValues={
                ":status": status,
                ":updated": datetime.now().isoformat(),
            },
        )
        return True
    except Exception as e:
        print(f"Error updating waitlist status: {e}")
        return False


def notify_waitlist(room_id):
    """Notify users on waitlist when room becomes available"""
    waitlist = get_room_waitlist(room_id)
    notified = []

    for entry in waitlist[:5]:  # Notify first 5 users
        user_id = entry.get("user_id")
        # Create notification
        notification_data = {
            "notification_id": str(uuid.uuid4()),
            "user_id": user_id,
            "type": "waitlist_available",
            "title": "Room Available!",
            "message": f"A room you're interested in is now available: {entry.get('room_name', 'Room')}",
            "room_id": room_id,
            "status": "pending",
            "created_at": datetime.now().isoformat(),
        }
        add_notification(notification_data)
        notified.append(user_id)

    return notified


# ============================================================================
# SERVICE BOOKINGS (Spa, Restaurant, Transportation, etc.)
# ============================================================================


def add_service(service_data):
    """Add a new service"""
    if not DYNAMODB_AVAILABLE:
        mock_services.append(service_data)
        return True

    try:
        table = dynamodb.Table(SERVICES_TABLE)
        table.put_item(Item=service_data)
        return True
    except Exception as e:
        print(f"Error adding service: {e}")
        return False


def get_services(branch_id=None, service_type=None):
    """Get available services"""
    if not DYNAMODB_AVAILABLE:
        services = mock_services
        if branch_id:
            services = [s for s in services if s.get("branch_id") == branch_id]
        if service_type:
            services = [s for s in services if s.get("service_type") == service_type]
        return services

    try:
        table = dynamodb.Table(SERVICES_TABLE)
        if branch_id:
            response = table.query(
                IndexName="BranchServicesIndex",
                KeyConditionExpression=Key("branch_id").eq(branch_id),
            )
            services = response.get("Items", [])
        else:
            response = table.scan()
            services = response.get("Items", [])

        if service_type:
            services = [s for s in services if s.get("service_type") == service_type]

        return services
    except Exception as e:
        print(f"Error getting services: {e}")
        return []


def book_service(service_booking_data):
    """Book a service"""
    if not DYNAMODB_AVAILABLE:
        mock_service_bookings.append(service_booking_data)
        return True

    try:
        table = dynamodb.Table(SERVICE_BOOKINGS_TABLE)
        table.put_item(Item=service_booking_data)
        return True
    except Exception as e:
        print(f"Error booking service: {e}")
        return False


def get_user_service_bookings(user_id):
    """Get user's service bookings"""
    if not DYNAMODB_AVAILABLE:
        return [sb for sb in mock_service_bookings if sb.get("user_id") == user_id]

    try:
        table = dynamodb.Table(SERVICE_BOOKINGS_TABLE)
        response = table.query(
            IndexName="UserServiceBookingsIndex",
            KeyConditionExpression=Key("user_id").eq(user_id),
        )
        return response.get("Items", [])
    except Exception as e:
        print(f"Error getting user service bookings: {e}")
        return []


def init_default_services(branch_id):
    """Initialize default services for a branch"""
    default_services = [
        {
            "service_id": str(uuid.uuid4()),
            "branch_id": branch_id,
            "service_type": "spa",
            "name": "Relaxing Spa Session",
            "description": "Full body massage and spa treatment",
            "price": 2500,
            "duration_minutes": 90,
            "available": True,
            "created_at": datetime.now().isoformat(),
        },
        {
            "service_id": str(uuid.uuid4()),
            "branch_id": branch_id,
            "service_type": "restaurant",
            "name": "Fine Dining Restaurant",
            "description": "Premium dining experience",
            "price": 1500,
            "duration_minutes": 120,
            "available": True,
            "created_at": datetime.now().isoformat(),
        },
        {
            "service_id": str(uuid.uuid4()),
            "branch_id": branch_id,
            "service_type": "transportation",
            "name": "Airport Pickup/Drop",
            "description": "Comfortable airport transfer",
            "price": 1000,
            "duration_minutes": 60,
            "available": True,
            "created_at": datetime.now().isoformat(),
        },
        {
            "service_id": str(uuid.uuid4()),
            "branch_id": branch_id,
            "service_type": "tour",
            "name": "City Tour Package",
            "description": "Guided tour of local attractions",
            "price": 3000,
            "duration_minutes": 480,
            "available": True,
            "created_at": datetime.now().isoformat(),
        },
        {
            "service_id": str(uuid.uuid4()),
            "branch_id": branch_id,
            "service_type": "laundry",
            "name": "Laundry Service",
            "description": "Express laundry and dry cleaning",
            "price": 500,
            "duration_minutes": 180,
            "available": True,
            "created_at": datetime.now().isoformat(),
        },
    ]

    for service in default_services:
        add_service(service)

    return len(default_services)


# ============================================================================
# NOTIFICATIONS SYSTEM
# ============================================================================


def add_notification(notification_data):
    """Add a notification"""
    if not DYNAMODB_AVAILABLE:
        mock_notifications.append(notification_data)
        return True

    try:
        table = dynamodb.Table(NOTIFICATIONS_TABLE)
        table.put_item(Item=notification_data)
        return True
    except Exception as e:
        print(f"Error adding notification: {e}")
        return False


def get_user_notifications(user_id, status=None):
    """Get user notifications"""
    if not DYNAMODB_AVAILABLE:
        notifications = [n for n in mock_notifications if n.get("user_id") == user_id]
        if status:
            notifications = [n for n in notifications if n.get("status") == status]
        return notifications

    try:
        table = dynamodb.Table(NOTIFICATIONS_TABLE)
        response = table.query(
            IndexName="UserNotificationsIndex",
            KeyConditionExpression=Key("user_id").eq(user_id),
        )
        notifications = response.get("Items", [])
        if status:
            notifications = [n for n in notifications if n.get("status") == status]
        return notifications
    except Exception as e:
        print(f"Error getting user notifications: {e}")
        return []


def mark_notification_sent(notification_id):
    """Mark notification as sent"""
    if not DYNAMODB_AVAILABLE:
        for n in mock_notifications:
            if n.get("notification_id") == notification_id:
                n["status"] = "sent"
                n["sent_at"] = datetime.now().isoformat()
                return True
        return False

    try:
        table = dynamodb.Table(NOTIFICATIONS_TABLE)
        table.update_item(
            Key={"notification_id": notification_id},
            UpdateExpression="SET #status = :status, sent_at = :sent",
            ExpressionAttributeNames={"#status": "status"},
            ExpressionAttributeValues={
                ":status": "sent",
                ":sent": datetime.now().isoformat(),
            },
        )
        return True
    except Exception as e:
        print(f"Error marking notification as sent: {e}")
        return False


def schedule_booking_reminders(booking_id, user_id, check_in_date, guest_email):
    """Schedule automated reminders for a booking"""
    try:
        check_in = (
            datetime.strptime(check_in_date, "%Y-%m-%d")
            if isinstance(check_in_date, str)
            else check_in_date
        )

        # 24-hour check-in reminder
        reminder_time = check_in - timedelta(days=1)
        if reminder_time > datetime.now():
            add_notification(
                {
                    "notification_id": str(uuid.uuid4()),
                    "user_id": user_id,
                    "booking_id": booking_id,
                    "type": "check_in_reminder",
                    "title": "Check-in Tomorrow!",
                    "message": f"Your stay begins tomorrow. Check-in time is 2:00 PM.",
                    "email": guest_email,
                    "scheduled_for": reminder_time.isoformat(),
                    "status": "pending",
                    "created_at": datetime.now().isoformat(),
                }
            )

        return True
    except Exception as e:
        print(f"Error scheduling booking reminders: {e}")
        return False


# Initialize sample data on module load
add_sample_data()
# Initialize Indian branches
init_indian_branches()
# Populate rooms with images
populate_rooms_with_images()
