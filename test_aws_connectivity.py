#!/usr/bin/env python3
"""
AWS Connectivity Test Script for Blissful Abodes
This script tests connectivity to all required AWS services
"""

import sys
import boto3
from botocore.exceptions import ClientError, NoCredentialsError
from datetime import datetime

# Configuration
REGION = 'us-east-1'
REQUIRED_TABLES = ['Users', 'AdminUsers', 'Projects', 'Enrollments']

# Color codes for terminal output
GREEN = '\033[92m'
RED = '\033[91m'
YELLOW = '\033[93m'
BLUE = '\033[94m'
RESET = '\033[0m'

def print_header(text):
    """Print section header"""
    print("\n" + "="*70)
    print(f"{BLUE}{text}{RESET}")
    print("="*70 + "\n")

def print_success(text):
    """Print success message"""
    print(f"{GREEN}✓ {text}{RESET}")

def print_error(text):
    """Print error message"""
    print(f"{RED}✗ {text}{RESET}")

def print_warning(text):
    """Print warning message"""
    print(f"{YELLOW}⚠ {text}{RESET}")

def print_info(text):
    """Print info message"""
    print(f"{BLUE}ℹ {text}{RESET}")

def test_aws_credentials():
    """Test AWS credentials and identity"""
    print_header("Testing AWS Credentials")

    try:
        sts = boto3.client('sts', region_name=REGION)
        identity = sts.get_caller_identity()

        print_success("AWS credentials configured correctly")
        print(f"  Account ID: {identity['Account']}")
        print(f"  User ARN: {identity['Arn']}")
        print(f"  Region: {REGION}")
        return True

    except NoCredentialsError:
        print_error("No AWS credentials found")
        print("  Please configure AWS credentials or attach IAM role to EC2")
        return False
    except ClientError as e:
        print_error(f"Error testing credentials: {e}")
        return False

def test_dynamodb_connection():
    """Test DynamoDB connection"""
    print_header("Testing DynamoDB Connection")

    try:
        dynamodb = boto3.client('dynamodb', region_name=REGION)

        # List all tables
        response = dynamodb.list_tables()
        all_tables = response.get('TableNames', [])

        print_success(f"Connected to DynamoDB successfully")
        print(f"  Total tables in region: {len(all_tables)}")

        # Check required tables
        print("\nChecking required tables:")
        all_exist = True

        for table_name in REQUIRED_TABLES:
            if table_name in all_tables:
                # Get table details
                try:
                    table_info = dynamodb.describe_table(TableName=table_name)
                    status = table_info['Table']['TableStatus']
                    item_count = table_info['Table']['ItemCount']

                    if status == 'ACTIVE':
                        print_success(f"{table_name} - Status: {status}, Items: {item_count}")
                    else:
                        print_warning(f"{table_name} - Status: {status}")

                except ClientError as e:
                    print_error(f"{table_name} - Error getting details: {e}")
                    all_exist = False
            else:
                print_error(f"{table_name} - NOT FOUND")
                all_exist = False

        if not all_exist:
            print("\n" + "="*70)
            print_warning("Some required tables are missing!")
            print("Run: python3 create_dynamodb_tables.py --create")
            print("="*70)
            return False

        return True

    except ClientError as e:
        print_error(f"Failed to connect to DynamoDB: {e}")
        print("  Check IAM permissions for DynamoDB")
        return False

def test_dynamodb_operations():
    """Test DynamoDB read/write operations"""
    print_header("Testing DynamoDB Operations")

    try:
        dynamodb = boto3.resource('dynamodb', region_name=REGION)
        table = dynamodb.Table('Users')

        # Test write
        test_username = f"test_user_{datetime.now().strftime('%Y%m%d%H%M%S')}"
        print(f"Testing write operation with user: {test_username}")

        table.put_item(
            Item={
                'username': test_username,
                'password': 'test_password',
                'test_record': True
            }
        )
        print_success("Write operation successful")

        # Test read
        print("Testing read operation...")
        response = table.get_item(
            Key={'username': test_username}
        )

        if 'Item' in response:
            print_success("Read operation successful")
        else:
            print_error("Read operation failed - item not found")
            return False

        # Test delete (cleanup)
        print("Cleaning up test record...")
        table.delete_item(
            Key={'username': test_username}
        )
        print_success("Delete operation successful")

        return True

    except ClientError as e:
        print_error(f"DynamoDB operations test failed: {e}")
        return False

def test_sns_connection():
    """Test SNS connection"""
    print_header("Testing SNS Connection")

    try:
        sns = boto3.client('sns', region_name=REGION)

        # List topics
        response = sns.list_topics()
        topics = response.get('Topics', [])

        print_success(f"Connected to SNS successfully")
        print(f"  Total topics in region: {len(topics)}")

        if topics:
            print("\nAvailable SNS Topics:")
            for topic in topics:
                topic_arn = topic['TopicArn']
                topic_name = topic_arn.split(':')[-1]

                # Get topic attributes
                try:
                    attrs = sns.get_topic_attributes(TopicArn=topic_arn)
                    subscriptions_confirmed = attrs['Attributes'].get('SubscriptionsConfirmed', '0')
                    subscriptions_pending = attrs['Attributes'].get('SubscriptionsPending', '0')

                    print(f"  • {topic_name}")
                    print(f"    ARN: {topic_arn}")
                    print(f"    Confirmed subscriptions: {subscriptions_confirmed}")
                    print(f"    Pending subscriptions: {subscriptions_pending}")

                except ClientError:
                    print(f"  • {topic_name}")
                    print(f"    ARN: {topic_arn}")
        else:
            print_warning("No SNS topics found")
            print("  Create SNS topic for notifications:")
            print("  aws sns create-topic --name BlissfulAbodes-Notifications")
            return False

        return True

    except ClientError as e:
        print_error(f"Failed to connect to SNS: {e}")
        print("  Check IAM permissions for SNS")
        return False

def test_sns_publish():
    """Test SNS publish capability"""
    print_header("Testing SNS Publish (Optional)")

    print_info("SNS publish test skipped to avoid sending notifications")
    print("  To test manually, update app_aws.py with correct SNS_TOPIC_ARN")
    print("  and trigger a notification event (e.g., user signup)")

    return True

def test_application_requirements():
    """Test Python packages required for the application"""
    print_header("Testing Application Requirements")

    required_packages = {
        'flask': 'Flask',
        'boto3': 'boto3',
        'werkzeug': 'Werkzeug',
        'botocore': 'botocore'
    }

    all_installed = True

    for package, display_name in required_packages.items():
        try:
            __import__(package)
            print_success(f"{display_name} is installed")
        except ImportError:
            print_error(f"{display_name} is NOT installed")
            all_installed = False

    if not all_installed:
        print("\n" + "="*70)
        print_warning("Some required packages are missing!")
        print("Install with: pip3 install flask boto3 werkzeug")
        print("="*70)

    return all_installed

def test_file_structure():
    """Test required files and directories exist"""
    print_header("Testing File Structure")

    import os

    required_items = {
        'app_aws.py': 'file',
        'templates': 'directory',
        'static': 'directory',
        'static/uploads': 'directory'
    }

    all_exist = True

    for item, item_type in required_items.items():
        if os.path.exists(item):
            if item_type == 'directory' and os.path.isdir(item):
                print_success(f"{item}/ (directory) exists")
            elif item_type == 'file' and os.path.isfile(item):
                print_success(f"{item} (file) exists")
            else:
                print_warning(f"{item} exists but wrong type")
                all_exist = False
        else:
            print_error(f"{item} NOT FOUND")
            all_exist = False

            if item_type == 'directory':
                print(f"  Create with: mkdir -p {item}")

    return all_exist

def display_summary(results):
    """Display test summary"""
    print("\n" + "="*70)
    print(f"{BLUE}TEST SUMMARY{RESET}")
    print("="*70 + "\n")

    total_tests = len(results)
    passed_tests = sum(1 for r in results.values() if r)
    failed_tests = total_tests - passed_tests

    for test_name, passed in results.items():
        if passed:
            print_success(f"{test_name}: PASSED")
        else:
            print_error(f"{test_name}: FAILED")

    print("\n" + "="*70)

    if failed_tests == 0:
        print_success(f"All {total_tests} tests passed! ✓")
        print(GREEN + "\nYour AWS environment is ready for deployment!" + RESET)
        print("\nNext steps:")
        print("1. Update app_aws.py with your SNS_TOPIC_ARN")
        print("2. Run: python3 app_aws.py")
        print("3. Access: http://YOUR-EC2-IP:5000")
    else:
        print_error(f"{failed_tests} out of {total_tests} tests failed")
        print(RED + "\nPlease fix the failed tests before deploying" + RESET)

    print("="*70 + "\n")

    return failed_tests == 0

def main():
    """Main test function"""
    print("\n" + "="*70)
    print(f"{BLUE}Blissful Abodes - AWS Connectivity Test{RESET}")
    print("="*70)
    print(f"Region: {REGION}")
    print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    # Run all tests
    results = {
        'AWS Credentials': test_aws_credentials(),
        'Application Requirements': test_application_requirements(),
        'File Structure': test_file_structure(),
        'DynamoDB Connection': test_dynamodb_connection(),
        'DynamoDB Operations': test_dynamodb_operations(),
        'SNS Connection': test_sns_connection(),
        'SNS Publish': test_sns_publish()
    }

    # Display summary
    all_passed = display_summary(results)

    # Exit with appropriate code
    sys.exit(0 if all_passed else 1)

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nTest interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n{RED}Unexpected error: {e}{RESET}")
        sys.exit(1)
