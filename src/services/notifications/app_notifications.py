import valkey
from src.root.abstract_base import AbstractBaseModel
from uuid import UUID
import firebase_admin
from firebase_admin import credentials


cred = credentials.Certificate("./AccountKey.json")
firebase_admin.initialize_app(cred)


class Notification(AbstractBaseModel):
    id: str
    type: str
    content: str
    timestamp: int


class AppStateUpdate(AbstractBaseModel):
    user_id: str
    device_token: str
    app_state: str  # "foreground" or "background"
    timestamp: int


class NotificationMessage(AbstractBaseModel):
    id: str
    title: str
    body: str
    image: str | None = None
    timestamp: int


class NotificationServiceError(Exception):
    """Custom exception for notification service errors."""

    pass


# Connect to Valkey running locally on default port
r = valkey.Valkey(host="localhost", port=6379, db=0)
pubsub = r.pubsub()
pubsub.subscribe("notifications")


def store_notification(user_id: str, notification: NotificationMessage):
    """Store a notification for a user."""
    r.rpush(f"user:{user_id}:notifications", notification.model_dump_json())


def get_notifications(user_id: str):
    """Retrieve all notifications for a user."""
    return r.lrange(f"user:{user_id}:notifications", 0, -1)


for message in pubsub.listen():
    if message["type"] == "message":
        print("Received:", message["data"].decode())


# streams not pubsub
stream_key = "notifications_stream"
last_id = "0-0"  # Start from the beginning
