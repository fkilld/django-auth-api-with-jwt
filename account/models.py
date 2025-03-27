# Import Django's models module which provides the base Model class and field types for database modeling
from django.db import models
# Import Django's built-in user management classes - BaseUserManager for custom user management and AbstractBaseUser for custom user model
from django.contrib.auth.models import BaseUserManager, AbstractBaseUser

# Define a custom User Manager class that extends Django's BaseUserManager to handle user creation and management operations


class UserManager(BaseUserManager):
    # Method to create a regular user account with basic permissions
    def create_user(self, email, name, tc, password=None, password2=None):
        """
        Creates and saves a regular User with the given email, name, tc and password.
        Args:
            email: User's email address (required)
            name: User's full name
            tc: Terms and conditions acceptance flag
            password: User's password
            password2: Password confirmation (not used currently)
        Returns:
            User object
        Raises:
            ValueError if email is not provided
        """
        # Validate that an email was provided since it's our primary identifier
        if not email:
            raise ValueError('User must have an email address')

        # Create a new user instance with normalized email (lowercase domain part)
        # The self.model refers to the User model that this manager is managing
        user = self.model(
            # Normalize email to ensure consistency
            email=self.normalize_email(email),
            name=name,  # Store the user's full name
            tc=tc,  # Store terms & conditions acceptance status
        )

        # Set the user's password using Django's password hashing mechanism for security
        user.set_password(password)
        # Save the user to the database, using the default database if multiple are configured
        user.save(using=self._db)
        # Return the created user object
        return user

    # Method to create a superuser (admin) account with full permissions
    def create_superuser(self, email, name, tc, password=None):
        """
        Creates and saves a superuser (admin) with the given email, name, tc and password.
        Uses create_user() but additionally sets is_admin=True
        Args:
            email: Superuser's email address
            name: Superuser's full name  
            tc: Terms and conditions acceptance
            password: Superuser's password
        Returns:
            User object with admin privileges
        """
        # Create a regular user first using the create_user method
        user = self.create_user(
            email,  # Pass email as identifier
            password=password,  # Pass password for authentication
            name=name,  # Pass name for user profile
            tc=tc,  # Pass terms acceptance status
        )
        # Set admin status to True to grant administrative privileges
        user.is_admin = True
        # Save the updated user object to the database
        user.save(using=self._db)
        # Return the created superuser object
        return user

# Define custom User Model that extends Django's AbstractBaseUser for customized authentication


class User(AbstractBaseUser):
    # Define email field as the main identifier for users instead of username
    email = models.EmailField(
        verbose_name='Email',  # Human-readable name for the field
        max_length=255,  # Maximum length of email addresses
        unique=True,  # Ensure each email can only be used once
    )
    # Define name field to store user's full name
    name = models.CharField(max_length=200)  # Allow names up to 200 characters
    # Boolean field to track acceptance of terms and conditions
    tc = models.BooleanField()  # Terms & Conditions acceptance flag

    # Boolean field to control whether user can log in
    # New accounts are active by default
    is_active = models.BooleanField(default=True)
    # Boolean field to identify admin users
    # New accounts are not admin by default
    is_admin = models.BooleanField(default=False)

    # Automatic timestamp field for user creation date
    # Set automatically when user is created
    created_at = models.DateTimeField(auto_now_add=True)
    # Automatic timestamp field that updates whenever the user object is saved
    # Updates automatically on each save
    updated_at = models.DateTimeField(auto_now=True)

    # Connect this model to our custom UserManager for user operations
    objects = UserManager()

    # Specify which field to use as the unique identifier for authentication
    USERNAME_FIELD = 'email'  # Use email for login instead of traditional username
    # List additional fields required when creating a superuser
    # These fields must be provided when creating superuser
    REQUIRED_FIELDS = ['name', 'tc']

    # String representation of the user object
    def __str__(self):
        """String representation of user - returns email address"""
        return self.email

    # Method to check if user has specific permission
    def has_perm(self, perm, obj=None):
        """
        Check if user has a specific permission.
        Currently returns True if user is admin, implementing a simple permission system.
        """
        return self.is_admin

    # Method to check if user has permission to access admin modules
    def has_module_perms(self, app_label):
        """
        Check if user has permissions to view the app `app_label`.
        Currently returns True if user is admin, granting full module access to admins.
        """
        return True

    # Property decorator to make this method accessible as a property
    @property
    def is_staff(self):
        """
        Check if user is staff member.
        Currently returns True if user is admin, making all admins staff members.
        Required by Django admin interface.
        """
        return self.is_admin
