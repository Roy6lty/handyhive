import valkey.exceptions
from fastapi import WebSocket
from src.root.database import db_dependency
from src.models import message_model
from src.database.handlers import message_handler
from uuid import UUID, uuid4
from datetime import datetime
import valkey

r = valkey.Valkey(host="localhost", port=6379, db=0)


async def send_message(
    db_conn: db_dependency, new_message: message_model.MessageDTO, user_id: UUID
):
    message = message_model.MessageCreate(
        content=new_message.message,
        sender_id=user_id,
        receiver_id=new_message.receiver_id,
    )
    _ = await message_handler.create_message(db_conn=db_conn, message=message)
    return None


async def get_user_messages(
    db_conn: db_dependency,
    user_id: UUID,
    receiver_id: UUID,
    last_sent: datetime | None = None,
):

    messages = await message_handler.get_messages_paginated_receiver_id(
        db_conn=db_conn, user_id=user_id, receiver_id=receiver_id
    )
    return messages


async def get_last_messages(db_conn: db_dependency, user_id: UUID):
    messages = await message_handler.get_last_messages(db_conn=db_conn, user_id=user_id)
    return messages


async def update_message_read_status(db_conn: db_dependency, id: UUID):
    await message_handler.update_messages_by_id(
        db_conn=db_conn, values=message_model.UpdateReadStatus(read=True), id=id
    )


async def delete_messages(db_conn: db_dependency, message_id: UUID):
    await message_handler.delete_message_by_id(db_conn=db_conn, id=message_id)


async def chat_message(
    websocket: WebSocket, db_conn: db_dependency, user_id: UUID, message_body: str
):
    try:
        r.xgroup_create(name=str(user_id), groupname=str(user_id), mkstream=True)
        print("stream and consumer group created")
        user_id_str = str(user_id)
        messages = await r.xreadgroup(
            groupname=user_id_str,
            consumername=user_id_str,
            streams={user_id_str: ">"},
            block=5000,
        )
        new_message = []
        for stream_name, entries in messages:
            for message_id, message_data in entries:
                print(f"Recieved message ID {message_data}")
                sender = message_data.get("sender")
                content = message_data.get("content")
                timestamp = message_data.get("timestamp", 1000) / 1000.0

                # Acknowledge the message
                r.xack(user_id_str, user_id_str, message_id)
                message_dict = message_model.MessageResponse(
                    id=uuid4(), body=content, sender=sender, timestamp=timestamp
                )
                await websocket.send_text(message_dict.model_dump_json())
                new_message.append(message_dict)

    except valkey.exceptions.ResponseError as e:
        if "BUSYGROUP" in str(e):
            print("Consumer group already exists")
        else:
            raise e
