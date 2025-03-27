# Import Response class from rest_framework to send custom API responses with data and status codes
from rest_framework.response import Response
# Import status module from rest_framework to use HTTP status codes like 200, 201, 404 etc.
from rest_framework import status
# Import APIView class which is the base class for creating class-based API views in DRF
from rest_framework.views import APIView
# Import all required serializer classes from account.serializers to handle data validation and conversion
from account.serializers import SendPasswordResetEmailSerializer, UserChangePasswordSerializer, UserLoginSerializer, UserPasswordResetSerializer, UserProfileSerializer, UserRegistrationSerializer
# Import authenticate function from django.contrib.auth to verify user credentials during login
from django.contrib.auth import authenticate
# Import custom UserRenderer class to format JSON responses consistently across the app
from account.renderers import UserRenderer
# Import RefreshToken from simplejwt to generate JWT tokens for authentication
from rest_framework_simplejwt.tokens import RefreshToken
# Import IsAuthenticated permission class to restrict views to only authenticated users
from rest_framework.permissions import IsAuthenticated

# Function to manually generate JWT tokens for a given user
# This function is used during registration and login to create authentication tokens


def get_tokens_for_user(user):
    # Create a new refresh token for the provided user using SimpleJWT's RefreshToken
    # The for_user() method automatically associates the token with the user
    refresh = RefreshToken.for_user(user)

    # Return a dictionary containing both the refresh and access tokens
    # The refresh token is used to obtain new access tokens when they expire
    # The access token is used for authenticating API requests
    return {
        # Convert refresh token to string for JSON serialization
        'refresh': str(refresh),
        # Get the access token from refresh token and convert to string
        # Access tokens have a shorter lifetime for security
        'access': str(refresh.access_token),
    }
# Define UserRegistrationView class that inherits from APIView to handle user registration requests


class UserRegistrationView(APIView):
    # Specify UserRenderer as the renderer class to format JSON responses consistently
    # This ensures errors and success responses follow the same structure
    renderer_classes = [UserRenderer]

    # Define post method to handle POST requests for user registration
    # Parameters:
    #   request: Contains the request data including user details
    #   format: Specifies the format of the response (defaults to None)
    def post(self, request, format=None):
        # Create UserRegistrationSerializer instance with the request data
        # This will validate and serialize the incoming user registration data
        serializer = UserRegistrationSerializer(data=request.data)

        # Check if the serializer data is valid according to defined rules
        # raise_exception=True will automatically return validation errors if data is invalid
        serializer.is_valid(raise_exception=True)

        # Save the validated user data to create a new user instance in the database
        # The save() method is implemented in the serializer to handle user creation
        user = serializer.save()

        # Generate JWT tokens (access and refresh) for the newly created user
        # These tokens will be used for authenticating subsequent requests
        token = get_tokens_for_user(user)

        # Return success response with the generated tokens and success message
        # HTTP 201 CREATED status code indicates successful resource creation
        return Response({'token': token, 'msg': 'Registration Successful'}, status=status.HTTP_201_CREATED)
# Define UserLoginView class that inherits from APIView to handle user login functionality
# APIView provides a clean way to implement API endpoints with proper HTTP method handling


class UserLoginView(APIView):
    # Specify UserRenderer as the renderer class to format JSON responses consistently
    # This ensures that both success and error responses follow the same structure defined in UserRenderer
    renderer_classes = [UserRenderer]

    # Define post method to handle POST requests for user login
    # Parameters:
    #   request: Contains the request data including login credentials
    #   format: Specifies the format of the response (defaults to None)
    def post(self, request, format=None):
        # Create UserLoginSerializer instance with the request data
        # This serializer will validate and process the login credentials
        serializer = UserLoginSerializer(data=request.data)

        # Validate the serializer data according to defined rules in UserLoginSerializer
        # raise_exception=True will automatically return validation errors if data is invalid
        serializer.is_valid(raise_exception=True)

        # Extract email from validated serializer data
        # Using get() method provides safe access to the data dictionary
        email = serializer.data.get('email')

        # Extract password from validated serializer data
        # Password will be used to authenticate the user
        password = serializer.data.get('password')

        # Attempt to authenticate user with provided email and password
        # authenticate() returns None if credentials are invalid
        user = authenticate(email=email, password=password)

        # Check if authentication was successful (user object exists)
        if user is not None:
            # Generate JWT tokens (access and refresh) for the authenticated user
            # These tokens will be used for subsequent request authentication
            token = get_tokens_for_user(user)

            # Return success response with tokens and success message
            # HTTP 200 OK status indicates successful request
            return Response({'token': token, 'msg': 'Login Success'}, status=status.HTTP_200_OK)
        else:
            # Return error response if authentication failed
            # HTTP 404 NOT FOUND status indicates invalid credentials
            # Structured error response includes field-level error message
            return Response({'errors': {'non_field_errors': ['Email or Password is not Valid']}}, status=status.HTTP_404_NOT_FOUND)

# Define UserProfileView class that inherits from APIView to handle user profile viewing functionality
# APIView provides a structured way to create API endpoints with proper HTTP method handling


class UserProfileView(APIView):
    # Specify UserRenderer as the renderer class to ensure consistent JSON response formatting
    # UserRenderer handles both success and error responses with proper structure
    renderer_classes = [UserRenderer]
    # Set IsAuthenticated permission class to ensure only authenticated users can access this view
    # This protects the profile endpoint from unauthorized access
    permission_classes = [IsAuthenticated]
    # Define get method to handle GET requests for retrieving user profile data
    # Parameters:
    #   request: Contains the authenticated user's request data
    #   format: Specifies the response format (defaults to None for JSON)

    def get(self, request, format=None):
        # Create UserProfileSerializer instance with the authenticated user's data
        # This serializes the user object into JSON format with specified fields
        serializer = UserProfileSerializer(request.user)
        # Return serialized user data with HTTP 200 OK status
        # HTTP 200 indicates successful retrieval of the requested resource
        return Response(serializer.data, status=status.HTTP_200_OK)

# Define UserChangePasswordView class that inherits from APIView to handle password change functionality
# APIView provides a clean way to implement API endpoints with proper HTTP method handling


class UserChangePasswordView(APIView):
    # Specify UserRenderer as the renderer class to format JSON responses consistently
    # UserRenderer handles both success and error cases with proper structure
    renderer_classes = [UserRenderer]
    # Set IsAuthenticated permission to ensure only logged in users can change password
    # This prevents unauthorized access to password change functionality
    permission_classes = [IsAuthenticated]
    # Define post method to handle POST requests for password changes
    # Parameters:
    #   request: Contains the user's request data including new password
    #   format: Specifies response format (defaults to None for JSON)

    def post(self, request, format=None):
        # Create UserChangePasswordSerializer instance with request data and user context
        # The serializer will validate the new password and handle the change
        # Context provides the current user object needed for password update
        serializer = UserChangePasswordSerializer(
            data=request.data, context={'user': request.user})
        # Validate serializer data and raise exception if invalid
        # This ensures password meets requirements before processing
        serializer.is_valid(raise_exception=True)
        # Return success response with 200 OK status after password change
        # HTTP 200 indicates the request was successful
        return Response({'msg': 'Password Changed Successfully'}, status=status.HTTP_200_OK)

# Define SendPasswordResetEmailView class that inherits from APIView to handle password reset email functionality
# This view initiates the password reset process by sending reset link via email


class SendPasswordResetEmailView(APIView):
    # Specify UserRenderer for consistent JSON response formatting
    # Ensures error and success responses follow the same structure
    renderer_classes = [UserRenderer]
    # Define post method to handle POST requests for password reset emails
    # Parameters:
    #   request: Contains user's email for password reset
    #   format: Specifies response format (defaults to None for JSON)

    def post(self, request, format=None):
        # Create SendPasswordResetEmailSerializer with request data
        # This serializer validates email and handles reset link generation
        serializer = SendPasswordResetEmailSerializer(data=request.data)
        # Validate the email and raise exception if invalid
        # Ensures email exists in system before sending reset link
        serializer.is_valid(raise_exception=True)
        # Return success response with 200 OK status after sending reset email
        # Message informs user to check their email for the reset link
        return Response({'msg': 'Password Reset link send. Please check your Email'}, status=status.HTTP_200_OK)
# Define UserPasswordResetView class that inherits from APIView to handle the actual password reset functionality
# This view processes the password reset request after user clicks the reset link from their email


class UserPasswordResetView(APIView):
    # Specify UserRenderer as the renderer class to ensure consistent JSON response formatting
    # UserRenderer handles both success and error responses with proper structure and UTF-8 encoding
    renderer_classes = [UserRenderer]

    # Define post method to handle POST requests for password reset
    # Parameters:
    #   request: Contains the new password data from user
    #   uid: Encrypted user ID from reset link to identify the user
    #   token: Security token from reset link to verify reset request authenticity
    #   format: Specifies response format (defaults to None for JSON)
    def post(self, request, uid, token, format=None):
        # Create UserPasswordResetSerializer instance with request data and context
        # Context includes uid and token needed to validate reset request and identify user
        # The serializer will handle password validation and actual reset operation
        serializer = UserPasswordResetSerializer(
            data=request.data, context={'uid': uid, 'token': token})

        # Validate serializer data and raise exception if invalid
        # This ensures new password meets requirements and reset token is valid
        # raise_exception=True will automatically return error responses if validation fails
        serializer.is_valid(raise_exception=True)

        # Return success response with HTTP 200 OK status after password reset
        # HTTP 200 indicates the request was successful and password has been reset
        # Include success message to inform user that reset was completed
        return Response({'msg': 'Password Reset Successfully'}, status=status.HTTP_200_OK)
