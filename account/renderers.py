# Import the renderers module from Django REST framework which provides base classes and utilities for converting
# Python objects into various response formats. We need this to customize how our API responses are formatted
from rest_framework import renderers

# Import the json module from Python's standard library which provides methods to encode Python objects into JSON
# strings and decode JSON strings back into Python objects. This is essential for API responses
import json

# Define a custom renderer class that inherits from JSONRenderer to control how our API formats JSON responses
# We create this custom class to have consistent response formats across our API, especially for error handling


class UserRenderer(renderers.JSONRenderer):
    # Set the character encoding to UTF-8 to ensure proper handling of all Unicode characters including special
    # characters and emojis. This is important for international compatibility and proper text rendering
    charset = 'utf-8'

    # Override the render method from JSONRenderer to customize how data is converted to JSON
    # This method is called automatically by DRF when preparing the API response
    # data: The Python object to be rendered (could be dict, list, etc.)
    # accepted_media_type: The content type that the client will accept (unused but required by parent class)
    # renderer_context: Additional rendering context from DRF (unused but required by parent class)
    def render(self, data, accepted_media_type=None, renderer_context=None):
        # Initialize an empty string to store our JSON response
        # We start with empty string because we'll build the response based on the data type
        response = ''

        # Check if the data contains any error details by converting it to string and checking for 'ErrorDetail'
        # DRF uses ErrorDetail objects to represent validation errors and other API exceptions
        # This helps us distinguish between successful responses and error responses
        if 'ErrorDetail' in str(data):
            # If errors exist, wrap the error data in an object with 'errors' key for consistent error formatting
            # This makes it easier for clients to handle errors uniformly
            response = json.dumps({'errors': data})
        else:
            # For successful responses, simply convert the data to JSON string as-is
            # This preserves the original structure of successful responses
            response = json.dumps(data)

        # Return the final JSON string that will be sent to the client
        # This could be either an error response or a success response
        return response
