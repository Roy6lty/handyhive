from src.root.abstract_base import AbstractBaseModel
from uuid import UUID


class CreateNotifications(AbstractBaseModel):
    title: str
    body: str
    image: str | None = None
    timestamp: int
    read: bool = False
    user_id: str
