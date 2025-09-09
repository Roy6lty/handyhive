import asyncio
from fastapi import FastAPI, Request, Response, HTTPException, WebSocketException
from fastapi.responses import JSONResponse
from src.root.logger import error_logger, log_to_file
import traceback
import sys
import uuid
from typing import Optional


class ExceptionLoggingMiddlewareConfig:
    """Configuration for the exception logging middleware."""

    def __init__(self, print_to_console: bool = True):
        self.print_to_console = print_to_console


async def exception_logging_middleware(
    request: Request,
    call_next,
    config: Optional[ExceptionLoggingMiddlewareConfig] = None,
):
    """
    Middleware to log exceptions that occur during request processing,
    including the filename and line number of the error.

    Args:
        request: The incoming request object.
        call_next: The function to call to process the request and get the response.
        config (Optional[ExceptionLoggingMiddlewareConfig]): Configuration for the middleware.

    Returns:
        The response object, or a JSONResponse with error details if an exception occurs.
    """
    if config is None:
        config = ExceptionLoggingMiddlewareConfig()  # Default to printing to console

    event_id = str(uuid.uuid4())  # Generate a unique ID for the event
    try:
        response: Response = await call_next(request)
        return response
    except HTTPException as exc:

        # Re-raise HTTPException to allow FastAPI's default handler to process it.
        # This ensures the correct status code and details are returned to the client.
        raise exc
    except WebSocketException as exc:
        raise exc

    except Exception as error:
        # Get the traceback information

        exc_type, exc_value, exc_traceback = sys.exc_info()

        if exc_traceback is not None:
            tb = traceback.extract_tb(exc_traceback)[-1]
            filename, line_number, func_name, text = tb
            full_traceback = traceback.format_exc()
            # Log the full stack trace with the filename and line number
            error_logger.error(
                {
                    "event_id": event_id,
                    "message": f"An unhandled exception occurred in {filename} (line {line_number}): {error}",
                    "filename": filename,
                    "line_number": line_number,
                    "func_name": func_name,
                    "request_url": request.url,
                }
            )

            error_logger.error(
                {
                    "event_id": event_id,
                    "message": full_traceback,
                    "request_url": request.url,
                }
            )

            # Conditionally print to console
            if config.print_to_console:
                print(
                    f"An unhandled exception occurred in {filename} (line {line_number}): {error}"
                )
                print(full_traceback)
                print(f"--- End of Exception (Event ID: {event_id}) ---\n")

        else:
            error_logger.error(
                {
                    "event_id": event_id,
                    "message": f"An unhandled exception occurred: {error}",
                    "request_url": request.url,
                }
            )
            error_logger.error(
                {
                    "event_id": event_id,
                    "message": "No traceback available.",
                    "request_url": request.url,
                }
            )
            # Conditionally print to console
            if config.print_to_console:
                print(f"An unhandled exception occurred: {error}")
                print("No traceback available.")

        # Log to file
        asyncio.create_task(
            log_to_file(error_message=error, request=request, event_id=event_id)
        )
        # return a json object if an error occurrence.

        return JSONResponse(
            status_code=500,
            content={"detail": "Service is unavailable. Please try again later."},
        )


def add_exception_middleware(
    app: FastAPI, config: Optional[ExceptionLoggingMiddlewareConfig] = None
):
    """Add exception_logging_middleware to the app's middleware stack.

    Args:
        app: The FastAPI app.
        config (Optional[ExceptionLoggingMiddlewareConfig]): Configuration for the middleware.
    """
    app.middleware("http")(
        lambda request, call_next: exception_logging_middleware(
            request, call_next, config
        )
    )
