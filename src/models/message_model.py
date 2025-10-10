from src.root.abstract_base import AbstractBaseModel
from uuid import UUID
from datetime import datetime


class MessageDTO(AbstractBaseModel):
    receiver_id: UUID
    message: str


class UpdateMessageDTO(AbstractBaseModel):
    body: str


class MessageCreate(AbstractBaseModel):
    profile_pic: str | None = None
    content: str
    sender_id: UUID
    receiver_id: UUID


class UpdateReadStatus(AbstractBaseModel):
    read: bool = False


class MessageWS(AbstractBaseModel):
    body: str


class MessageResponse(AbstractBaseModel):
    id: UUID
    sender: UUID
    body: str
    date_created: datetime | None = None
    timestamp: int = 0
