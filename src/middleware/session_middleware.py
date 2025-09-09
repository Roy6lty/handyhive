from fastapi import FastAPI
from starlette.middleware.sessions import SessionMiddleware


def add_session_middleware(app: FastAPI, secret_key: str):
    """
    Adds SessionMiddleware to the FastAPI application.

    Args:
        app: The FastAPI app.
        secret_key: The secret key for the session middleware.
    """
    # Use app.add_middleware to correctly add the SessionMiddleware
    app.add_middleware(
        SessionMiddleware,
        secret_key=secret_key,
        https_only=True,
        same_site="lax",
    )
