# Import the admin module from django.contrib to access Django's admin interface functionality
from django.contrib import admin
# Import our custom User model from the account app's models.py
from account.models import User
# Import the base UserAdmin class that we'll extend to customize the admin interface
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

# Create a custom admin class for our User model that inherits from Django's base UserAdmin
# This allows us to customize how the User model is displayed and edited in the admin interface


class UserModelAdmin(BaseUserAdmin):
    # Define which fields should be displayed in the list view of users
    # Shows user ID, email, name, terms & conditions acceptance status, and admin status
    # This helps administrators quickly view important user information
    list_display = ('id', 'email', 'name', 'tc', 'is_admin')

    # Add filters to the right sidebar of the admin interface
    # Allows filtering users by their admin status for easier management
    list_filter = ('is_admin',)

    # Define how fields are grouped and displayed when editing an existing user
    # Organizes user data into logical sections for better usability
    fieldsets = (
        # Group for login credentials (email and password)
        ('User Credentials', {'fields': ('email', 'password')}),
        # Group for personal information (name and terms & conditions acceptance)
        ('Personal info', {'fields': ('name', 'tc')}),
        # Group for administrative permissions
        ('Permissions', {'fields': ('is_admin',)}),
    )

    # Define fields shown when adding a new user through the admin interface
    # This is separate from fieldsets because new users need different fields
    add_fieldsets = (
        (None, {
            # 'wide' class makes the form wider for better visibility
            'classes': ('wide',),
            # Fields required when creating a new user, including both password fields
            'fields': ('email', 'name', 'tc', 'password1', 'password2'),
        }),
    )

    # Enable search functionality for users by their email
    # This helps administrators find specific users quickly
    search_fields = ('email',)

    # Define the default ordering of users in the list view
    # Orders by email first, then by ID for consistent display
    ordering = ('email', 'id')

    # Required empty tuple for the UserAdmin class
    # Used for many-to-many fields, which our User model doesn't have
    filter_horizontal = ()


# Register our custom User model with the admin site using our UserModelAdmin class
# This makes the User model accessible through Django's admin interface
admin.site.register(User, UserModelAdmin)
