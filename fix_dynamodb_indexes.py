import boto3
import time
from botocore.exceptions import ClientError


def update_tables():
    print("Connecting to DynamoDB to fix missing indexes...")
    dynamodb = boto3.client("dynamodb", region_name="us-east-1")

    # 1. Fix blissful_bookings
    table_name = "blissful_bookings"
    index_name = "UserBookingsIndex"
    try:
        response = dynamodb.describe_table(TableName=table_name)
        existing_indexes = [
            i["IndexName"] for i in response["Table"].get("GlobalSecondaryIndexes", [])
        ]

        if index_name not in existing_indexes:
            print(f"Adding {index_name} to {table_name}...")
            dynamodb.update_table(
                TableName=table_name,
                AttributeDefinitions=[
                    {"AttributeName": "user_id", "AttributeType": "S"}
                ],
                GlobalSecondaryIndexUpdates=[
                    {
                        "Create": {
                            "IndexName": index_name,
                            "KeySchema": [
                                {"AttributeName": "user_id", "KeyType": "HASH"}
                            ],
                            "Projection": {"ProjectionType": "ALL"},
                            "ProvisionedThroughput": {
                                "ReadCapacityUnits": 5,
                                "WriteCapacityUnits": 5,
                            },
                        }
                    }
                ],
            )
            print("Request sent.")
        else:
            print(f"{index_name} already exists on {table_name}.")

        # Check for RoomBookingsIndex while we are at it
        if "RoomBookingsIndex" not in existing_indexes:
            # We can only do one GSI update at a time per table usually, but let's check.
            # If we just sent a request, we can't send another immediately.
            pass

    except Exception as e:
        print(f"Error checking {table_name}: {e}")

    # 2. Fix blissful_reviews
    table_name = "blissful_reviews"
    index_name = "UserReviewsIndex"
    try:
        response = dynamodb.describe_table(TableName=table_name)
        existing_indexes = [
            i["IndexName"] for i in response["Table"].get("GlobalSecondaryIndexes", [])
        ]

        if index_name not in existing_indexes:
            print(f"Adding {index_name} to {table_name}...")
            dynamodb.update_table(
                TableName=table_name,
                AttributeDefinitions=[
                    {"AttributeName": "user_id", "AttributeType": "S"}
                ],
                GlobalSecondaryIndexUpdates=[
                    {
                        "Create": {
                            "IndexName": index_name,
                            "KeySchema": [
                                {"AttributeName": "user_id", "KeyType": "HASH"}
                            ],
                            "Projection": {"ProjectionType": "ALL"},
                            "ProvisionedThroughput": {
                                "ReadCapacityUnits": 5,
                                "WriteCapacityUnits": 5,
                            },
                        }
                    }
                ],
            )
            print("Request sent.")
        else:
            print(f"{index_name} already exists on {table_name}.")

    except Exception as e:
        print(f"Error checking {table_name}: {e}")

    # 3. Fix blissful_pricing_rules
    table_name = "blissful_pricing_rules"
    index_name = "BranchRulesIndex"
    try:
        response = dynamodb.describe_table(TableName=table_name)
        existing_indexes = [
            i["IndexName"] for i in response["Table"].get("GlobalSecondaryIndexes", [])
        ]

        if index_name not in existing_indexes:
            print(f"Adding {index_name} to {table_name}...")
            dynamodb.update_table(
                TableName=table_name,
                AttributeDefinitions=[
                    {"AttributeName": "branch_id", "AttributeType": "S"}
                ],
                GlobalSecondaryIndexUpdates=[
                    {
                        "Create": {
                            "IndexName": index_name,
                            "KeySchema": [
                                {"AttributeName": "branch_id", "KeyType": "HASH"}
                            ],
                            "Projection": {"ProjectionType": "ALL"},
                            "ProvisionedThroughput": {
                                "ReadCapacityUnits": 5,
                                "WriteCapacityUnits": 5,
                            },
                        }
                    }
                ],
            )
            print("Request sent.")
        else:
            print(f"{index_name} already exists on {table_name}.")

    except Exception as e:
        print(f"Error checking {table_name}: {e}")


if __name__ == "__main__":
    update_tables()
