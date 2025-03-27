# Import admin module from django.contrib to enable Django's built-in admin interface functionality
from django.contrib import admin
# Import path and include functions from django.urls - path is used to define individual URL patterns,
# while include allows referencing URLs from other apps
from django.urls import path, include

# Define the list of URL patterns for the entire project
urlpatterns = [
    # Map the admin/ URL to Django's built-in admin site interface
    # This provides an out-of-the-box admin panel for managing database records
    path('admin/', admin.site.urls),
    
    # Include all URLs from the account app under the api/user/ prefix
    # This creates a namespace for all authentication/user management related URLs
    # The actual URL patterns are defined in account/urls.py
    path('api/user/', include('account.urls'))
]
