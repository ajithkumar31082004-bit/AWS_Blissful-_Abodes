import boto3
from botocore.exceptions import ClientError
import sys

# AWS Configuration
REGION = 'us-east-1'

# Initialize DynamoDB resource
dynamodb = boto3.resource('dynamodb', region_name=REGION)
dynamodb_client = boto3.client('dynamodb', region_name=REGION)

def create_users_table():
    """Create Users table"""
    try:
        table = dynamodb.create_table(
            TableName='Users',
            KeySchema=[
                {
                    'AttributeName': 'username',
                    'KeyType': 'HASH'  # Partition key
                }
            ],
            AttributeDefinitions=[
                {
                    'AttributeName': 'username',
                    'AttributeType': 'S'
                }
            ],
            BillingMode='PAY_PER_REQUEST',  # On-Demand billing
            Tags=[
                {
                    'Key': 'Application',
                    'Value': 'BlissfulAbodes'
                },
                {
                    'Key': 'Environment',
                    'Value': 'Production'
                }
            ]
        )
        print(f"✓ Creating Users table... ", end='')
        table.wait_until_exists()
        print("SUCCESS")
        return True
    except ClientError as e:
        if e.response['Error']['Code'] == 'ResourceInUseException':
            print("✓ Users table already exists")
            return True
        else:
            print(f"✗ Error creating Users table: {e}")
            return False

def create_admin_users_table():
    """Create AdminUsers table"""
    try:
        table = dynamodb.create_table(
            TableName='AdminUsers',
            KeySchema=[
                {
                    'AttributeName': 'username',
                    'KeyType': 'HASH'  # Partition key
                }
            ],
            AttributeDefinitions=[
                {
                    'AttributeName': 'username',
                    'AttributeType': 'S'
                }
            ],
            BillingMode='PAY_PER_REQUEST',
            Tags=[
                {
                    'Key': 'Application',
                    'Value': 'BlissfulAbodes'
                },
                {
                    'Key': 'Environment',
                    'Value': 'Production'
                }
            ]
        )
        print(f"✓ Creating AdminUsers table... ", end='')
        table.wait_until_exists()
        print("SUCCESS")
        return True
    except ClientError as e:
        if e.response['Error']['Code'] == 'ResourceInUseException':
            print("✓ AdminUsers table already exists")
            return True
        else:
            print(f"✗ Error creating AdminUsers table: {e}")
            return False

def create_projects_table():
    """Create Projects table"""
    try:
        table = dynamodb.create_table(
            TableName='Projects',
            KeySchema=[
                {
                    'AttributeName': 'id',
                    'KeyType': 'HASH'  # Partition key
                }
            ],
            AttributeDefinitions=[
                {
                    'AttributeName': 'id',
                    'AttributeType': 'S'
                }
            ],
            BillingMode='PAY_PER_REQUEST',
            Tags=[
                {
                    'Key': 'Application',
                    'Value': 'BlissfulAbodes'
                },
                {
                    'Key': 'Environment',
                    'Value': 'Production'
                }
            ]
        )
        print(f"✓ Creating Projects table... ", end='')
        table.wait_until_exists()
        print("SUCCESS")
        return True
    except ClientError as e:
        if e.response['Error']['Code'] == 'ResourceInUseException':
            print("✓ Projects table already exists")
            return True
        else:
            print(f"✗ Error creating Projects table: {e}")
            return False

def create_enrollments_table():
    """Create Enrollments table"""
    try:
        table = dynamodb.create_table(
            TableName='Enrollments',
            KeySchema=[
                {
                    'AttributeName': 'username',
                    'KeyType': 'HASH'  # Partition key
                }
            ],
            AttributeDefinitions=[
                {
                    'AttributeName': 'username',
                    'AttributeType': 'S'
                }
            ],
            BillingMode='PAY_PER_REQUEST',
            Tags=[
                {
                    'Key': 'Application',
                    'Value': 'BlissfulAbodes'
                },
                {
                    'Key': 'Environment',
                    'Value': 'Production'
                }
            ]
        )
        print(f"✓ Creating Enrollments table... ", end='')
        table.wait_until_exists()
        print("SUCCESS")
        return True
    except ClientError as e:
        if e.response['Error']['Code'] == 'ResourceInUseException':
            print("✓ Enrollments table already exists")
            return True
        else:
            print(f"✗ Error creating Enrollments table: {e}")
            return False

def verify_tables():
    """Verify all tables exist and are active"""
    print("\n" + "="*60)
    print("VERIFYING DYNAMODB TABLES")
    print("="*60 + "\n")

    tables_to_check = ['Users', 'AdminUsers', 'Projects', 'Enrollments']
    all_tables_exist = True

    for table_name in tables_to_check:
        try:
            table = dynamodb.Table(table_name)
            table.load()
            status = table.table_status
            item_count = table.item_count

            print(f"✓ {table_name}")
            print(f"  - Status: {status}")
            print(f"  - Items: {item_count}")
            print(f"  - ARN: {table.table_arn}")
            print()

        except ClientError as e:
            if e.response['Error']['Code'] == 'ResourceNotFoundException':
                print(f"✗ {table_name} - NOT FOUND")
                all_tables_exist = False
            else:
                print(f"✗ {table_name} - ERROR: {e}")
                all_tables_exist = False

    return all_tables_exist

def list_all_tables():
    """List all DynamoDB tables in the region"""
    try:
        response = dynamodb_client.list_tables()
        tables = response.get('TableNames', [])

        print("\n" + "="*60)
        print(f"ALL DYNAMODB TABLES IN REGION: {REGION}")
        print("="*60)

        if tables:
            for i, table in enumerate(tables, 1):
                print(f"{i}. {table}")
        else:
            print("No tables found in this region")

        print()

    except ClientError as e:
        print(f"Error listing tables: {e}")

def delete_all_tables():
    """Delete all Blissful Abodes tables (use with caution!)"""
    print("\n" + "="*60)
    print("WARNING: DELETING ALL TABLES")
    print("="*60 + "\n")

    confirmation = input("Are you sure you want to DELETE all tables? Type 'DELETE' to confirm: ")

    if confirmation != 'DELETE':
        print("Deletion cancelled.")
        return

    tables_to_delete = ['Users', 'AdminUsers', 'Projects', 'Enrollments']

    for table_name in tables_to_delete:
        try:
            table = dynamodb.Table(table_name)
            table.delete()
            print(f"✓ Deleting {table_name}... ", end='')
            table.wait_until_not_exists()
            print("DELETED")
        except ClientError as e:
            if e.response['Error']['Code'] == 'ResourceNotFoundException':
                print(f"✓ {table_name} does not exist")
            else:
                print(f"✗ Error deleting {table_name}: {e}")

def create_all_tables():
    """Create all required DynamoDB tables"""
    print("\n" + "="*60)
    print("CREATING DYNAMODB TABLES FOR BLISSFUL ABODES")
    print("="*60 + "\n")

    results = []
    results.append(create_users_table())
    results.append(create_admin_users_table())
    results.append(create_projects_table())
    results.append(create_enrollments_table())

    if all(results):
        print("\n✓ All tables created successfully!")
        return True
    else:
        print("\n✗ Some tables failed to create")
        return False

def show_help():
    """Show help message"""
    print("\n" + "="*60)
    print("DYNAMODB TABLE MANAGEMENT SCRIPT")
    print("="*60 + "\n")
    print("Usage: python create_dynamodb_tables.py [option]")
    print("\nOptions:")
    print("  --create     Create all DynamoDB tables")
    print("  --verify     Verify all tables exist and show details")
    print("  --list       List all tables in the region")
    print("  --delete     Delete all Blissful Abodes tables (WARNING!)")
    print("  --help       Show this help message")
    print("\nExamples:")
    print("  python create_dynamodb_tables.py --create")
    print("  python create_dynamodb_tables.py --verify")
    print()

def main():
    """Main function"""
    # Check if AWS credentials are configured
    try:
        sts = boto3.client('sts', region_name=REGION)
        identity = sts.get_caller_identity()
        print(f"\n✓ Connected to AWS")
        print(f"  Account ID: {identity['Account']}")
        print(f"  Region: {REGION}")
        print(f"  User ARN: {identity['Arn']}\n")
    except Exception as e:
        print(f"\n✗ Error connecting to AWS: {e}")
        print("\nPlease ensure:")
        print("1. AWS credentials are configured (IAM role on EC2 or AWS CLI credentials)")
        print("2. You have permissions for DynamoDB operations")
        print("3. The region is correct\n")
        sys.exit(1)

    # Parse command line arguments
    if len(sys.argv) > 1:
        option = sys.argv[1].lower()

        if option == '--create':
            create_all_tables()
            verify_tables()
        elif option == '--verify':
            verify_tables()
        elif option == '--list':
            list_all_tables()
        elif option == '--delete':
            delete_all_tables()
        elif option == '--help' or option == '-h':
            show_help()
        else:
            print(f"Unknown option: {option}")
            show_help()
    else:
        # Default behavior: create and verify
        create_all_tables()
        verify_tables()
        list_all_tables()

if __name__ == '__main__':
    main()
