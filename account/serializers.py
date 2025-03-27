# Import Django REST framework's serializers module which provides tools and classes for converting complex data types like Django models into Python data types that can be easily rendered into JSON/XML
from rest_framework import serializers
# Import our custom User model from the local account app that we defined to handle user authentication and management
from account.models import User
# Import Django's text encoding utilities - smart_str for intelligent string conversion, force_bytes for converting to bytes, and DjangoUnicodeDecodeError for handling encoding errors
from django.utils.encoding import smart_str, force_bytes, DjangoUnicodeDecodeError
# Import Django's URL-safe base64 encoding/decoding utilities used for encoding user IDs in password reset URLs to make them safe for email transmission
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
# Import Django's built-in token generator that creates unique tokens for password reset verification to ensure security
from django.contrib.auth.tokens import PasswordResetTokenGenerator
# Import our custom Util class that contains helper methods like email sending functionality
from account.utils import Util


# Define a serializer class for user registration that inherits from ModelSerializer to automatically handle model fields
class UserRegistrationSerializer(serializers.ModelSerializer):
    # Define an additional password confirmation field that isn't part of the User model
    # style={'input_type':'password'} renders this as a password field in HTML forms for security
    # write_only=True ensures this sensitive field is never included in API responses
    password2 = serializers.CharField(
        style={'input_type': 'password'}, write_only=True)

    # Meta class provides configuration for the serializer, defining how model instances should be converted to/from JSON
    class Meta:
        # Specify that this serializer works with our custom User model
        model = User
        # List all fields that should be included when serializing/deserializing
        # email - For user identification and login
        # name - Store user's full name
        # password - For account security
        # password2 - For password confirmation during registration
        # tc - Terms and conditions acceptance tracking
        fields = ['email', 'name', 'password', 'password2', 'tc']
        # Additional field-specific configurations
        # Setting password as write_only prevents it from being included in responses for security
        extra_kwargs = {
            'password': {'write_only': True}
        }

    # Custom validation method that runs after individual field validation
    # Ensures password and confirmation password match before allowing registration
    def validate(self, attrs):
        # Get the password value from the validated data dictionary
        password = attrs.get('password')
        # Get the confirmation password value from the validated data dictionary
        password2 = attrs.get('password2')

        # Compare the two passwords and raise a validation error if they don't match
        # This ensures users don't make typos when entering their password
        if password != password2:
            raise serializers.ValidationError(
                "Password and Confirm Password doesn't match")

        # Return the validated data if all validation passes
        return attrs

    # Override the create method to properly handle user creation using our custom UserManager
    # This ensures passwords are properly hashed and stored securely
    def create(self, validate_data):
        # Use our custom create_user method from UserManager instead of default model creation
        # Unpack validated data as keyword arguments to create the user with all provided fields
        return User.objects.create_user(**validate_data)

# Define a serializer class specifically for handling user login functionality
# We use ModelSerializer to automatically handle model fields and validation
# This serializer will convert login form data to Python objects and vice versa


class UserLoginSerializer(serializers.ModelSerializer):
    # Define a custom email field that will be used to identify the user during login
    # EmailField ensures proper email format validation
    # max_length=255 matches the User model's email field length
    # This field is required and will be validated against the database
    email = serializers.EmailField(max_length=255)

    # Meta class provides configuration for the ModelSerializer
    # This inner class is required to specify model-specific settings
    class Meta:
        # Specify that this serializer works with our custom User model
        # This links the serializer to our User model for validation
        model = User

        # Define which fields should be included in the serialization process
        # 'email' - Used as the unique identifier for login
        # 'password' - For authenticating the user's credentials
        # These fields will be required in the login request
        fields = ['email', 'password']


# Define a serializer class specifically for handling and displaying user profile information
# This class inherits from ModelSerializer to automatically handle model fields and validation
# We use ModelSerializer instead of regular Serializer because it provides automatic field mapping from the User model
class UserProfileSerializer(serializers.ModelSerializer):
    # Define a nested Meta class that provides metadata and configuration for the serializer
    # The Meta class is a convention in Django that allows declaring model-specific settings
    class Meta:
        # Specify that this serializer should work with our custom User model
        # This creates a direct link between the serializer and our User model for proper field mapping
        model = User

        # Define which specific fields from the User model should be included in the serialized output
        # 'id' - Include the user's unique identifier for reference and linking
        # 'email' - Include the user's email address which serves as their username
        # 'name' - Include the user's full name for display purposes
        # We explicitly list only these fields for security (excluding password, tc, etc.)
        fields = ['id', 'email', 'name']

# Define a serializer class for handling password changes for authenticated users
# We inherit from Serializer instead of ModelSerializer since we're not mapping directly to a model
# This serializer handles the validation and processing of password change requests


class UserChangePasswordSerializer(serializers.Serializer):
    # Define a password field to accept the user's new password
    # max_length=255 ensures passwords aren't too long while allowing for complex passwords
    # style={'input_type': 'password'} renders this as a password field in forms/browsable API
    # write_only=True ensures passwords are never included in responses for security
    password = serializers.CharField(
        max_length=255, style={'input_type': 'password'}, write_only=True)

    # Define a confirmation password field to ensure user enters password correctly
    # Uses same constraints as password field for consistency
    # Having two fields helps prevent typos when entering new password
    password2 = serializers.CharField(
        max_length=255, style={'input_type': 'password'}, write_only=True)

    # Meta class defines serializer configuration and behavior
    # This provides Django with information about which fields to include
    class Meta:
        # Specify which fields should be included in serialized data
        # Both password fields are needed for validation
        fields = ['password', 'password2']

    # Custom validation method that runs after individual field validation
    # This method handles the business logic of changing the password
    def validate(self, attrs):
        # Extract the new password from the validated data dictionary
        # attrs contains the data after field-level validation
        password = attrs.get('password')

        # Extract the confirmation password from validated data
        # This will be compared with the first password to ensure they match
        password2 = attrs.get('password2')

        # Get the current user from the serializer's context
        # Context is passed from the view when the serializer is instantiated
        user = self.context.get('user')

        # Compare the two passwords to ensure they match
        # This prevents accidental typos when setting new password
        if password != password2:
            # Raise validation error if passwords don't match
            # This error will be caught by DRF and returned in the response
            raise serializers.ValidationError(
                "Password and Confirm Password doesn't match")

        # Use Django's built-in password hashing by calling set_password
        # This properly hashes the password before storing it
        user.set_password(password)

        # Save the user object to persist the new hashed password
        # This commits the change to the database
        user.save()

        # Return the validated data as required by DRF
        # This data could be used by subsequent processing
        return attrs


# Serializer class for handling password reset email requests
# This handles the first step of password reset where user requests reset link
class SendPasswordResetEmailSerializer(serializers.Serializer):
    # Define email field to accept user's email address
    # EmailField provides automatic email format validation
    # max_length matches User model's email field
    email = serializers.EmailField(max_length=255)

    # Meta class defines serializer configuration
    # This provides Django with information about which fields to include
    class Meta:
        # Only include email field in serialization
        # We only need email to identify user for password reset
        fields = ['email']

    # Custom validation method to process the reset email request
    # This method handles the logic of generating and sending reset link
    def validate(self, attrs):
        # Extract email from validated data
        # This email will be used to look up the user
        email = attrs.get('email')

        # Check if a user exists with this email address
        # filter() is used instead of get() to avoid exceptions
        if User.objects.filter(email=email).exists():
            # Retrieve the user object for this email
            # We can safely use get() here as we verified user exists
            user = User.objects.get(email=email)

            # Generate a URL-safe base64 encoded string of user's ID
            # This encoded ID will be used in reset link to identify user
            uid = urlsafe_base64_encode(force_bytes(user.id))

            # Print encoded UID for debugging purposes
            # This helps in development and troubleshooting
            print('Encoded UID', uid)

            # Generate unique token for password reset
            # This token ensures reset link can only be used once
            token = PasswordResetTokenGenerator().make_token(user)

            # Print token for debugging purposes
            # Helps verify token generation in development
            print('Password Reset Token', token)

            # Construct complete password reset link
            # Uses frontend URL with uid and token as parameters
            link = 'http://localhost:3000/api/user/reset/'+uid+'/'+token

            # Print complete reset link for debugging
            # Helps verify link construction in development
            print('Password Reset Link', link)

            # Create email body with reset link
            # Simple text format for email body
            body = 'Click Following Link to Reset Your Password '+link

            # Prepare email data dictionary
            # Contains all necessary information for sending email
            data = {
                'subject': 'Reset Your Password',  # Email subject line
                'body': body,                      # Email body with reset link
                'to_email': user.email            # Recipient's email address
            }

            # Email sending is commented out
            # Uncomment to enable actual email sending
            # Util.send_email(data)

            # Return validated data as required by DRF
            # This indicates successful processing
            return attrs
        else:
            # Raise validation error if email not found
            # This prevents revealing which emails are registered
            raise serializers.ValidationError('You are not a Registered User')

# This serializer class handles the password reset functionality by validating and processing
# the new password submission after a user clicks the reset link
# It inherits from serializers.Serializer to handle data validation and processing


class UserPasswordResetSerializer(serializers.Serializer):
    # Define the password field that will store the user's new password
    # max_length=255 prevents extremely long passwords that could cause issues
    # style={'input_type': 'password'} ensures the password is hidden in forms/UI
    # write_only=True means this field will never be included in serialized output for security
    password = serializers.CharField(
        max_length=255, style={'input_type': 'password'}, write_only=True)

    # Define the password confirmation field to ensure user types password correctly
    # Uses identical settings to password field since it serves same purpose
    # Having two fields helps prevent typos when setting new password
    password2 = serializers.CharField(
        max_length=255, style={'input_type': 'password'}, write_only=True)

    # Meta class defines metadata for the serializer
    # This is a Django convention for configuring class behavior
    class Meta:
        # Explicitly list which fields should be included in serialization
        # Only password and password2 are needed since this is specifically for password reset
        fields = ['password', 'password2']

    # validate() method is called automatically by DRF when validating submitted data
    # attrs contains all the submitted fields that passed field-level validation
    def validate(self, attrs):
        try:
            # Extract the new password from the validated data dictionary
            # Using get() method provides safe access in case field is missing
            password = attrs.get('password')

            # Extract the password confirmation value similarly
            password2 = attrs.get('password2')

            # Get the uid (user id) from the serializer's context
            # Context is set by the view and contains the encoded user id from reset URL
            uid = self.context.get('uid')

            # Get the reset token from context similarly
            # Token proves this is a valid reset attempt from email link
            token = self.context.get('token')

            # Compare passwords to ensure they match exactly
            # This is crucial for confirming user entered password correctly
            if password != password2:
                raise serializers.ValidationError(
                    "Password and Confirm Password doesn't match")

            # Decode the base64 encoded user id using Django's smart_str
            # urlsafe_base64_decode converts from URL-safe format back to binary
            # smart_str ensures proper string encoding of the decoded bytes
            id = smart_str(urlsafe_base64_decode(uid))

            # Retrieve the user object from database using decoded id
            # This confirms the user exists and gets their record for updating
            user = User.objects.get(id=id)

            # Verify the reset token is valid and not expired using Django's token generator
            # Returns False if token is invalid or expired for security
            if not PasswordResetTokenGenerator().check_token(user, token):
                raise serializers.ValidationError(
                    'Token is not Valid or Expired')

            # Set the user's new password using Django's password hashing
            # set_password() automatically handles proper password hashing
            user.set_password(password)

            # Save the updated user object to persist the new password
            # This commits the change to the database
            user.save()

            # Return the validated data as required by DRF
            # This indicates successful validation and processing
            return attrs

        # Handle case where the uid cannot be properly decoded
        # This could happen if URL was tampered with or corrupted
        except DjangoUnicodeDecodeError as identifier:
            # Attempt token verification again, though it will likely fail
            # This helps identify if token is the specific issue
            PasswordResetTokenGenerator().check_token(user, token)

            # Raise validation error to indicate invalid reset attempt
            # Generic message avoids revealing system details
            raise serializers.ValidationError('Token is not Valid or Expired')
