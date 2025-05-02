from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import (
    OpenApiExample,
    OpenApiParameter,
    OpenApiResponse,
    extend_schema,
)

import medialibrary.users.serializers as users_s

login_extend_schema = extend_schema(
    summary="User authentication",
    description="""
        Returns an authentication token and user data upon successful authentication.
        """,
    examples=[
        OpenApiExample(
            "Successful request example",
            value={"email": "user@example.com", "password": "password"},
            request_only=True,
        ),
        OpenApiExample(
            "Successful response example",
            value={
                "token": "9944b09199c62bcf9418ad846dd0e4bbdfc6ee4b",
                "user": {
                    "email": "user@example.com",
                    "username": "user",
                    "avatar": 1,
                },
            },
            response_only=True,
            status_codes=["200"],
        ),
        OpenApiExample(
            "Authentication failure example",
            value={"detail": "Invalid credentials"},
            response_only=True,
            status_codes=["401"],
        ),
    ],
    responses={
        200: OpenApiResponse(
            description="Authentication successful",
            response=users_s.UserSerializer,
        ),
        400: OpenApiResponse(
            description="Invalid input data",
            examples=[
                OpenApiExample(
                    "Validation error example",
                    value={
                        "email": ["This field is required."],
                        "password": ["This field is required."],
                    },
                )
            ],
        ),
        401: OpenApiResponse(
            description="Invalid credentials",
            examples=[
                OpenApiExample("Error example", value={"detail": "Invalid credentials"})
            ],
        ),
    },
)

register_extend_schema = extend_schema(
    summary="Register new user",
    description="""Creates a new user account and returns an authentication token.""",
    examples=[
        OpenApiExample(
            "Registration Request Example",
            value={
                "email": "user@example.com",
                "username": "user",
                "password1": "password",
                "password2": "password",
            },
            request_only=True,
        ),
        OpenApiExample(
            "Success Response Example",
            value={"token": "9944b09199c62bcf9418ad846dd0e4bbdfc6ee4b"},
            response_only=True,
        ),
    ],
    responses={
        201: OpenApiResponse(
            description="User created successfully", response=OpenApiTypes.OBJECT
        ),
        400: OpenApiResponse(
            description="Validation error",
            examples=[
                OpenApiExample("Error", value={"email": ["This field is required."]})
            ],
        ),
    },
)

change_password_extend_schema = extend_schema(
    summary="Change password",
    description="""Allows authenticated users to change their password.""",
    examples=[
        OpenApiExample(
            "Request Example",
            value={
                "old_password": "password",
                "new_password": "password",
                "current_password": "newpassword",
            },
            request_only=True,
        ),
        OpenApiExample(
            "Success Response",
            value={"detail": "Password changed successfully"},
            response_only=True,
        ),
    ],
    responses={
        200: OpenApiResponse(description="Password changed successfully"),
        400: OpenApiResponse(
            description="Validation error",
            examples=[
                OpenApiExample(
                    "Error",
                    value={
                        "confirm_password": ["Passwords must match."],
                    },
                )
            ],
        ),
        401: OpenApiResponse(
            description="Authentication credentials were not provided"
        ),
    },
)

reset_password_extend_schema = extend_schema(
    summary="Request password reset",
    description="""Initiates password reset process.
        Sends a reset link to the provided email address.
        Rate limited to 1 request per 10 minutes per IP address.""",
    examples=[
        OpenApiExample(
            "Request Example",
            value={"email": "user@example.com"},
            request_only=True,
        ),
        OpenApiExample(
            "Success Response", value={"detail": "Message sent"}, response_only=True
        ),
    ],
    responses={
        200: OpenApiResponse(description="Reset email sent if account exists"),
        400: OpenApiResponse(
            description="Validation error",
            examples=[
                OpenApiExample(
                    "Error", value={"email": ["Enter a valid email address."]}
                )
            ],
        ),
        403: OpenApiResponse(description="Too many requests (rate limited)"),
    },
)

reset_password_confirm_extend_schema = extend_schema(
    summary="Confirm password reset",
    description="""Finalizes password reset process using the token from email.
        This is typically accessed via link in the password reset email.""",
    parameters=[
        OpenApiParameter(
            name="token",
            type=OpenApiTypes.UUID,
            location=OpenApiParameter.PATH,
            description="Reset token from email",
        )
    ],
    responses={
        200: OpenApiResponse(description="Password was changed successfully"),
        400: OpenApiResponse(
            description="Invalid request",
            examples=[
                OpenApiExample("Error", value={"error": "Token is required"}),
                OpenApiExample("Error", value={"error": "Invalid or expired token"}),
            ],
        ),
        404: OpenApiResponse(
            description="Not found",
            examples=[OpenApiExample("Error", value={"error": "User not found"})],
        ),
    },
)
