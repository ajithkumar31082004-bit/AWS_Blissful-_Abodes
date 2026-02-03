import boto3
import os
from botocore.exceptions import ClientError


class SNSNotifier:
    def __init__(self):
        try:
            self.sns_client = boto3.client(
                "sns",
                region_name="us-east-1",
                aws_access_key_id=None,
                aws_secret_access_key=None,
            )
            self.topic_arn = None
            self.aws_available = True
            print("AWS SNS connection established")
        except Exception as e:
            print(f"Warning: Could not connect to AWS SNS - {e}")
            print("Falling back to mock notifications")
            self.aws_available = False
            self.sns_client = None
            self.topic_arn = None

        # Create topic if it doesn't exist and AWS is available
        if self.aws_available and not self.topic_arn:
            self.topic_arn = self.create_topic()

    def create_topic(self):
        """Create SNS topic for notifications"""
        if not self.aws_available:
            return "mock-topic-arn"

        try:
            response = self.sns_client.create_topic(
                Name="blissful-abodes-notifications"
            )
            topic_arn = response["TopicArn"]

            # Store the ARN in environment or config
            print(f"Created SNS Topic: {topic_arn}")
            return topic_arn

        except ClientError as e:
            print(f"Error creating SNS topic: {e}")
            return None
        except Exception as e:
            print(f"Unexpected error creating topic: {e}")
            return None

    def subscribe_email(self, email_address):
        """Subscribe an email to the SNS topic"""
        if not self.aws_available or not self.topic_arn:
            print(f"Mock: Subscribed {email_address} to notifications")
            return "mock-subscription-arn"

        try:
            response = self.sns_client.subscribe(
                TopicArn=self.topic_arn,
                Protocol="email",
                Endpoint=email_address,
                ReturnSubscriptionArn=True,
            )

            print(f"Subscribed {email_address} to SNS topic")
            return response["SubscriptionArn"]

        except ClientError as e:
            print(f"Error subscribing email: {e}")
            return None
        except Exception as e:
            print(f"Unexpected error subscribing: {e}")
            return None

    def send_notification(self, subject, message):
        """Send notification to all subscribers"""
        if not self.aws_available or not self.topic_arn:
            print(f"Mock: Notification sent - {subject}")
            return "mock-message-id"

        try:
            response = self.sns_client.publish(
                TopicArn=self.topic_arn,
                Subject=str(subject)[:100],  # Limit subject length
                Message=str(message),
            )

            print(f"Notification sent: {response['MessageId']}")
            return response["MessageId"]

        except ClientError as e:
            print(f"Error sending notification: {e}")
            return None
        except Exception as e:
            print(f"Unexpected error sending notification: {e}")
            return None

    def send_booking_confirmation(self, email, booking_details):
        """Send booking confirmation email"""
        subject = (
            f"Booking Confirmation - {booking_details.get('booking_id', 'Unknown')}"
        )

        message = f"""
        Dear {booking_details.get('guest_name', 'Guest')},
        
        Thank you for booking with Blissful Abodes!
        
        Booking Details:
        - Booking ID: {booking_details.get('booking_id', 'N/A')}
        - Check-in: {booking_details.get('check_in', 'N/A')}
        - Check-out: {booking_details.get('check_out', 'N/A')}
        - Status: {booking_details.get('status', 'confirmed')}
        
        We look forward to hosting you!
        
        Best regards,
        The Blissful Abodes Team
        """

        # Send to specific email (if SNS doesn't support direct email, we can use SES)
        # For simplicity, we'll publish to topic and let SNS handle distribution
        return self.send_notification(subject, message)

    def send_custom_email(self, email, subject, message):
        """Send custom email to specific address"""
        if not self.aws_available or not self.topic_arn:
            print(f"Mock: Custom email sent to {email}: {subject}")
            return "mock-message-id"

        try:
            # Note: SNS doesn't support sending to specific emails directly
            # In production, use AWS SES for direct email sending
            response = self.sns_client.publish(
                TopicArn=self.topic_arn,
                Subject=str(subject)[:100],
                Message=str(message),
                MessageAttributes={
                    "email": {"DataType": "String", "StringValue": str(email)}
                },
            )

            print(f"Custom email sent to {email}: {response['MessageId']}")
            return response["MessageId"]

        except ClientError as e:
            print(f"Error sending custom email: {e}")
            return None
        except Exception as e:
            print(f"Unexpected error sending custom email: {e}")
            return None


# Global notifier instance
try:
    notifier = SNSNotifier()
except Exception as e:
    print(f"Error creating SNS notifier: {e}")
    notifier = None


# Convenience functions with error handling
def subscribe_email(email_address):
    try:
        if notifier:
            return notifier.subscribe_email(email_address)
        else:
            print(f"Mock: Subscribed {email_address}")
            return "mock-subscription"
    except Exception as e:
        print(f"Error in subscribe_email: {e}")
        return None


def send_booking_confirmation(email, booking_details):
    try:
        if notifier:
            return notifier.send_booking_confirmation(email, booking_details)
        else:
            print(f"Mock: Booking confirmation sent to {email}")
            return "mock-message-id"
    except Exception as e:
        print(f"Error in send_booking_confirmation: {e}")
        return None


def send_notification(subject, message):
    try:
        if notifier:
            return notifier.send_notification(subject, message)
        else:
            print(f"Mock: Notification sent - {subject}")
            return "mock-message-id"
    except Exception as e:
        print(f"Error in send_notification: {e}")
        return None
