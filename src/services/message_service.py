import json
import time
import uuid
import hashlib
import asyncio
import valkey
from typing import Any
import valkey.exceptions
from fastapi import WebSocket
from src.root.database import db_dependency
from src.models import message_model
from src.database.handlers import message_handler, user_handler
from uuid import UUID, uuid4
from datetime import datetime

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


async def listener(websocket: WebSocket, pubsub: Any, channel_name: str, user_id: str):
    try:
        async for message in pubsub.listen():
            if message["type"] == "message":
                data = message["data"]
                if isinstance(data, bytes):
                    data = data.decode("utf-8")
                    data_json = json.loads(data)
                    if data_json["sender"] != str(user_id):
                        content = data_json["content"]
                        await websocket.send_text(content)
    except asyncio.CancelledError:
        await pubsub.unsubscribe(channel_name)


async def web_socket_message(
    websocket: WebSocket,
    db_conn: db_dependency,
    user_id: uuid.UUID,
    receiver_id: uuid.UUID,
):
    await websocket.accept()
    messages = await get_user_messages(
        db_conn=db_conn, user_id=user_id, receiver_id=receiver_id
    )
    user = await user_handler.get_user_by_id(db_conn=db_conn, user_id=user_id)
    profile_pic = user.profile_pic
    listener_task, channel_name = None, None

    try:
        for message in messages:
            await websocket.send_text(message.model_dump_json())

        sorted_uuids = sorted([str(receiver_id), str(token_info.id)])
        combined = "".join(sorted_uuids)
        pair_id = hashlib.sha256(combined.encode()).hexdigest()
        pubsub = r.pubsub()
        channel_name = pair_id
        await pubsub.subscribe(channel_name)

        listener_task = asyncio.create_task(
            listener(
                websocket=websocket,
                pubsub=pubsub,
                channel_name=channel_name,
                user_id=str(user_id),
            )
        )

        while True:
            # check if use is online
            data = await websocket.receive_text()
            pub_message = {
                "sender": str(user_id),
                "content": data,
                "timestamp": int(time.time() * 1000),
            }
            serialized = json.dumps(pub_message)
            try:
                await r.publish(channel_name, serialized)
            except Exception as e:
                print("Publish failed:", e)

            await message_handler.create_message(
                db_conn=db_conn,
                message=message_model.MessageCreate(
                    content=data,
                    sender_id=receiver_id,
                    receiver_id=user_id,
                    profile_pic=profile_pic,
                ),
            )
    except WebSocketDisconnect:
        if listener_task:
            listener_task.cancel()
        if channel_name:
            await pubsub.unsubscribe(channel_name)
        await r.close()
