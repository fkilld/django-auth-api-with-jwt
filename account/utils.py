# Import EmailMessage class from django.core.mail to handle email functionality
from django.core.mail import EmailMessage
# Import os module to access environment variables
import os

# Utility class containing helper methods


class Util:
    # Static method decorator - allows calling method without instantiating class
    @staticmethod
    # Method to send emails, takes a data dictionary containing email details
    def send_email(data):
        # Create EmailMessage instance with email parameters
        email = EmailMessage(
            # Set email subject from data dictionary
            subject=data['subject'],
            # Set email body/content from data dictionary
            body=data['body'],
            # Get sender email from environment variable for security
            from_email=os.environ.get('EMAIL_FROM'),
            # Set recipient email(s) as list from data dictionary
            to=[data['to_email']]
        )
        # Send the email using Django's email backend
        email.send()
