# DRF JWT Authentication System

A simple authentication system built with Django REST Framework (DRF) and JSON Web Tokens (JWT).

## Table of Contents
- [Setup](#setup)
- [Environment Variables](#environment-variables)
- [API Endpoints](#api-endpoints)
  - [Sign Up](#sign-up)
  - [Email Confirmation](#email-confirmation)
  - [Resend Verification Email](#resend-verification-email)
  - [Login](#login)
  - [Refresh Token](#refresh-token)
- [Usage Examples](#usage-examples)

## Setup

### Prerequisites
- Python 3.8+
- pip

### Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd <project-directory>
```

2. Create and activate a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Create a `.env` file in the root directory with the following variables:
```bash
SECRET_KEY=your-secret-key-here
TOKEN_EXPIRY=3600
EMAIL_HOST_USER="<your email here>"
EMAIL_HOST_PASSWORD="<your password>"
```
### Email Configuration

This project uses Gmail SMTP for sending emails. If you encounter issues sending emails, ensure that:

- **"Allow less secure apps"** is enabled in your Gmail account settings.  
   - Go to [Google Account Settings](https://myaccount.google.com/), navigate to **Security** > **Less secure app access**, and turn it on.

- If you have **Two-Factor Authentication (2FA)** enabled, create an **App Password**:
   - Go to [Google Account Settings](https://myaccount.google.com/), navigate to **Security** > **App passwords**, and generate a password for your app.

For more information, visit: [Google Support](https://support.google.com/accounts/answer/6010255).


5. Run migrations:
```bash
python manage.py migrate
```

6. Start the development server:
```bash
python manage.py runserver
```

## API Endpoints

### Sign Up
- **URL**: `/api/auth/signup/`
- **Method**: `POST`
- **Description**: Register a new user with email verification
- **Request Body**:
```json
{
    "email": "user@example.com",
    "password": "secure_password",
}
```
- **Success Response**:
  - **Code**: 201
  - **Content**:
```json
{
    "message": "User created successfully"
}
```
- **Error Response**:
  - **Code**: 400
  - **Content**:
```json
{
    "message": "failed to send verification email: [error details]"
}
```

### Email Confirmation
- **URL**: `/api/auth/confirm-email/<token>/`
- **Method**: `GET`
- **Description**: Confirm user's email using the verification token
- **URL Parameters**: `token=[string]`
- **Success Response**:
  - **Code**: 200
  - **Content**:
```json
{
    "message": "Email verified successfully!"
}
```
- **Error Responses**:
  - **Code**: 400
  - **Content**:
```json
{
    "message": "Token has expired. Request a new one."
}
```
  OR
```json
{
    "message": "Invalid token"
}
```
  OR
```json
{
    "message": "Email is already verified."
}
```

### Resend Verification Email
- **URL**: `/api/auth/resend-verification-email/`
- **Method**: `GET`
- **Description**: Resend verification email to user
- **Query Parameters**: `email=[string]`
- **Success Response**:
  - **Code**: 200
  - **Content**:
```json
{
    "message": "Verification email sent"
}
```
- **Error Responses**:
  - **Code**: 400
  - **Content**:
```json
{
    "message": "No email is provided"
}
```
  OR
```json
{
    "message": "Email is already verified."
}
```

### Login
- **URL**: `/api/auth/login/`
- **Method**: `POST`
- **Description**: Authenticate user and receive JWT tokens
- **Request Body**:
```json
{
    "email": "user@example.com",
    "password": "secure_password"
}
```
- **Success Response**:
  - **Code**: 200
  - **Content**:
```json
{
    "message": "Login successful",
    "access": "access_token_here",
    "refresh": "refresh_token_here"
}
```
- **Error Response**:
  - **Code**: 401
  - **Content**:
```json
{
    "message": "Invalid credentials"
}
```

### Refresh Token
- **URL**: `/api/auth/token/refresh/`
- **Method**: `POST`
- **Description**: Refresh JWT access token using a valid refresh token
- **Request Body**:
```json
{
    "refresh": "your-refresh-token-here"
}
```
- **Success Response**:
  - **Code**: 200
  - **Content**:
```json
{
    "access": "new-access-token-here"
}
```
- **Error Response**:
  - **Code**: 400
  - **Content**:
```json
{
    "message": "Invalid refresh token."
}
```

## Usage Examples

### Python Example using Requests
```python
import requests

BASE_URL = "http://localhost:8000/api/auth"

def signup_user(email, password, first_name, last_name):
    response = requests.post(f"{BASE_URL}/signup/", json={
        "email": email,
        "password": password,
        "first_name": first_name,
        "last_name": last_name
    })
    return response.json()

def login_user(email, password):
    response = requests.post(f"{BASE_URL}/login/", json={
        "email": email,
        "password": password
    })
    return response.json()

def refresh_access_token(refresh_token):
    response = requests.post(f"{BASE_URL}/token/refresh/", json={
        "refresh": refresh_token
    })
    return response.json()

def confirm_email(token):
    response = requests.get(f"{BASE_URL}/confirm-email/{token}/")
    return response.json()

def resend_verification(email):
    response = requests.get(f"{BASE_URL}/resend-verification-email/", 
                          params={"email": email})
    return response.json()
```

### cURL Examples

1. Sign Up:
```bash
curl -X POST http://localhost:8000/api/auth/signup/ \
     -H "Content-Type: application/json" \
     -d '{"email":"user@example.com","password":"secure_password","first_name":"John","last_name":"Doe"}'
```

2. Login:
```bash
curl -X POST http://localhost:8000/api/auth/login/ \
     -H "Content-Type: application/json" \
     -d '{"email":"user@example.com","password":"secure_password"}'
```

3. Refresh Token:
```bash
curl -X POST http://localhost:8000/api/auth/token/refresh/ \
     -H "Content-Type: application/json" \
     -d '{"refresh":"your-refresh-token-here"}'
```

4. Confirm Email:
```bash
curl -X GET http://localhost:8000/api/auth/confirm-email/your-token-here/
```

5. Resend Verification Email:
```bash
curl -X GET "http://localhost:8000/api/auth/resend-verification-email/?email=user@example.com"
```
