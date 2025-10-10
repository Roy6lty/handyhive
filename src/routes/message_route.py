import json
from time import time
from typing import Any
from datetime import datetime
import redis
import hashlib
import asyncio
import redis.asyncio as redis
from fastapi import (
    APIRouter,
    Depends,
    status,
    WebSocket,
    WebSocketDisconnect,
)
from uuid import UUID
from src.models.token_models import AccessTokenData
from src.services import message_service
from src.root.database import db_dependency
from src.models import message_model
from src.services.authorization_service import (
    get_user_verification_service,
    get_user_verification_service_ws,
)
from src.database.handlers import user_handler, message_handler
from exponent_server_sdk import PushClient, PushMessage
from src.root.env_settings import env


router = APIRouter(tags=["Message"], prefix="/api/v1/messages")

r = redis.Redis.from_url(env.REDIS_URL)


@router.get(
    "/{receiver_id}",
    description="Get User Messages Data",
    response_model=list[message_model.MessageResponse],
)
async def get_message(
    db_conn: db_dependency,
    last_sent: datetime | None = None,
    receiver_id=UUID,
    token_info: AccessTokenData = Depends(get_user_verification_service),
):
    if last_sent is None:
        last_sent = datetime(2000, 1, 1, 0, 0, 0)
    return await message_service.get_user_messages(
        db_conn=db_conn,
        user_id=token_info.id,
        receiver_id=receiver_id,
        last_sent=last_sent,
    )


@router.get(
    "/",
    description="Get User Messages Data",
    # response_model=list[message_model.MessageResponse],
)
async def get_all_last_message(
    db_conn: db_dependency,
    token_info: AccessTokenData = Depends(get_user_verification_service),
):

    return await message_service.get_last_messages(
        db_conn=db_conn,
        user_id=token_info.id,
    )


@router.post(
    "",
    description="Send Messages",
)
async def send_message(
    db_conn: db_dependency,
    new_message: message_model.MessageDTO,
    token_info: AccessTokenData = Depends(get_user_verification_service),
):
    return await message_service.send_message(
        db_conn=db_conn, user_id=token_info.id, new_message=new_message
    )


@router.patch("/{message_id}/status", description="update message read status")
async def update_message_status(db_conn: db_dependency, message_id: UUID):
    return await message_service.update_message_read_status(
        db_conn=db_conn, id=message_id
    )


@router.delete(
    "",
    description="Delete Message",
    status_code=status.HTTP_202_ACCEPTED,
)
async def delete_user_account(
    db_conn: db_dependency,
    message_id: UUID,
    _: AccessTokenData = Depends(get_user_verification_service),
):
    return await message_service.delete_messages(db_conn=db_conn, message_id=message_id)


@router.websocket("/{receiver_id}/chat")
async def websocket_endpoint(
    websocket: WebSocket,
    receiver_id: UUID,
    db_conn: db_dependency,
    token_info: AccessTokenData = Depends(get_user_verification_service_ws),
):
    # send me the time of your last message
    await websocket.accept()
    messages = await message_service.get_user_messages(
        db_conn=db_conn, user_id=token_info.id, receiver_id=receiver_id
    )
    user = await user_handler.get_user_by_id(db_conn=db_conn, user_id=token_info.id)
    profile_pic = user.profile_pic
    print(messages)
    push_client = PushClient()
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
        print(channel_name)

        async def listener(
            websocket: WebSocket, pubsub: Any, channel_name: str, user_id: str
        ):
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

        listener_task = asyncio.create_task(
            listener(
                websocket=websocket,
                pubsub=pubsub,
                channel_name=channel_name,
                user_id=str(token_info.id),
            )
        )

        while True:
            # check if use is online
            data = await websocket.receive_text()
            pub_message = {
                "sender": str(token_info.id),
                "content": data,
                "timestamp": int(time() * 1000),
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
                    receiver_id=token_info.id,
                    profile_pic=profile_pic,
                ),
            )
            # message = PushMessage(
            #     to="token",
            #     title="message",
            #     body=data,
            #     data={},
            #     subtitle="message",
            #     sound="default",
            #     priority="normal",
            #     channel_id="chat--updates",
            #     badge=1,
            #     mutable_content=True,
            #     expiration=int(time() + 360000),
            #     ttl=int(time() + 3600),
            #     display_in_foreground=True,
            #     category="message",
            # )
            # response = push_client.publish(message)
    except WebSocketDisconnect:
        if listener_task:
            listener_task.cancel()
        if channel_name:
            await pubsub.unsubscribe(channel_name)
        await r.close()
