<<<<<<< HEAD
# Django REST Framework Authentication API with JWT
=======

>>>>>>> b1e699e5e63043d1ec42a97ad24222b0451595ae

This project implements a complete authentication system using Django REST Framework and Simple JWT. It provides secure user registration, login, profile management, and password reset functionality through RESTful APIs.

## Features

- User Registration with email verification
- JWT Authentication
- User Login/Logout
- Password Change (for logged in users) 
- Password Reset via Email
- User Profile Management
        
## API Endpoints

### Authentication Endpoints
- `POST /api/user/register/` - Register new user
- `POST /api/user/login/` - Login user and receive JWT tokens
- `GET /api/user/profile/` - Get user profile (requires authentication)
- `POST /api/user/changepassword/` - Change password (requires authentication)

### Password Reset Flow
- `POST /api/user/send-reset-password-email/` - Request password reset email
- `POST /api/user/reset-password/<uid>/<token>/` - Reset password with token

## Project Setup

1. Create and activate virtual environment:
