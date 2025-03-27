# Import the path function from django.urls module which is essential for defining URL routing patterns
# path() function takes URL pattern, view and name as arguments to create URL configurations
from django.urls import path

# Import all the view classes needed for handling different user authentication and management features
# These view classes contain the actual logic for processing requests and returning responses
# SendPasswordResetEmailView - Handles sending password reset emails to users
# UserChangePasswordView - Handles password change requests for logged in users
# UserLoginView - Handles user authentication and login
# UserProfileView - Handles retrieving and updating user profile information
# UserRegistrationView - Handles new user registration
# UserPasswordResetView - Handles resetting forgotten passwords with reset tokens
from account.views import SendPasswordResetEmailView, UserChangePasswordView, UserLoginView, UserProfileView, UserRegistrationView, UserPasswordResetView

# Define the urlpatterns list which Django uses to match URLs to views
# This list contains all URL patterns for the account app functionality
urlpatterns = [
    # URL pattern for user registration endpoint
    # When /register/ is accessed, UserRegistrationView.as_view() handles the request
    # name='register' allows reverse URL lookups in other parts of code
    path('register/', UserRegistrationView.as_view(), name='register'),

    # URL pattern for user login endpoint
    # When /login/ is accessed, UserLoginView.as_view() handles authentication
    # name='login' enables referring to this URL pattern by name elsewhere
    path('login/', UserLoginView.as_view(), name='login'),

    # URL pattern for user profile endpoint
    # When /profile/ is accessed, UserProfileView.as_view() handles profile operations
    # name='profile' allows reverse URL resolution using the name
    path('profile/', UserProfileView.as_view(), name='profile'),

    # URL pattern for password change endpoint (for logged in users)
    # When /changepassword/ is accessed, UserChangePasswordView.as_view() processes the request
    # name='changepassword' enables referring to this URL by name
    path('changepassword/', UserChangePasswordView.as_view(), name='changepassword'),

    # URL pattern for initiating password reset via email
    # When /send-reset-password-email/ is accessed, SendPasswordResetEmailView.as_view() sends reset email
    # name='send-reset-password-email' allows reverse URL lookups
    path('send-reset-password-email/', SendPasswordResetEmailView.as_view(),
         name='send-reset-password-email'),

    # URL pattern for password reset confirmation with dynamic parameters
    # <uid> captures the user ID and <token> captures the reset token from the URL
    # When accessed, UserPasswordResetView.as_view() validates token and processes reset
    # name='reset-password' enables referring to this URL pattern by name
    path('reset-password/<uid>/<token>/',
         UserPasswordResetView.as_view(), name='reset-password'),

]
