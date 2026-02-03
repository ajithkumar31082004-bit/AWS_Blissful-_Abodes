import boto3
from botocore.exceptions import ClientError


def reset_and_seed_rooms():
    dynamodb = boto3.resource("dynamodb", region_name="us-east-1")
    table_name = "blissful_rooms"

    try:
        table = dynamodb.Table(table_name)

        # 1. Scan and Delete all items
        print(f"Scanning {table_name} to delete all items...")
        response = table.scan()
        items = response.get("Items", [])

        with table.batch_writer() as batch:
            for i, item in enumerate(items):
                batch.delete_item(Key={"room_id": item["room_id"]})
                if i % 100 == 0:
                    print(f"Deleted {i} items...")

        while "LastEvaluatedKey" in response:
            response = table.scan(ExclusiveStartKey=response["LastEvaluatedKey"])
            items = response.get("Items", [])
            with table.batch_writer() as batch:
                for item in items:
                    batch.delete_item(Key={"room_id": item["room_id"]})

        print("All existing rooms deleted successfully.")

    except ClientError as e:
        print(f"Error accessing table: {e}")
    except Exception as e:
        print(f"An error occurred: {e}")


if __name__ == "__main__":
    reset_and_seed_rooms()
