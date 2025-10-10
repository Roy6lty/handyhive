import select
import uuid
from src.database.orms import user_orm
from src.root.database import db_dependency
from sqlalchemy import select, update, delete, func, and_
from sqlalchemy.orm import joinedload
from src.custom_exceptions import error
from src.models import orm_models
from src.models import message_model


async def create_message(db_conn: db_dependency, message: message_model.MessageCreate):
    new_message = user_orm.MessagesTable(
        id=uuid.uuid4(), user_id=message.sender_id, **message.model_dump()
    )
    db_conn.add(new_message)
    await db_conn.commit()
    await db_conn.refresh(new_message)

    return orm_models.MessageTableModel.model_validate(new_message)


async def get_messages_paginated(db_conn: db_dependency, user_id: uuid.UUID):
    query = (
        select(user_orm.MessagesTable)
        .where(user_orm.MessagesTable.id == user_id)
        .limit(50)
        .order_by(user_orm.MessagesTable.date_created)
    )
    result = await db_conn.execute(query)
    messages = result.scalars().all()

    if messages:
        return [
            orm_models.MessageTableModel.model_validate(message) for message in messages
        ]
    else:
        return []


async def get_last_messages(db_conn: db_dependency, user_id: uuid.UUID):
    query = (
        select(
            user_orm.MessagesTable.id,
            user_orm.MessagesTable.sender_id,
            user_orm.MessagesTable.receiver_id,
            user_orm.MessagesTable.content,
            user_orm.MessagesTable.date_created,
            func.row_number()
            .over(
                partition_by=user_orm.MessagesTable.receiver_id,
                order_by=user_orm.MessagesTable.date_created.desc(),
            )
            .label("rnk"),
        )
        .where(
            user_orm.MessagesTable.sender_id == user_id,
            user_orm.MessagesTable.read == False,
        )
        .subquery()
    )

    final_query = (
        select(user_orm.MessagesTable)
        .join(query, user_orm.MessagesTable.id == query.c.id)
        .where(query.c.rnk == 1)
    )
    result = await db_conn.execute(final_query)
    results = result.scalars().all()

    return results


async def get_messages_paginated_receiver_id(
    db_conn: db_dependency, user_id: uuid.UUID, receiver_id: uuid.UUID
):
    query = (
        select(user_orm.MessagesTable)
        .where(
            and_(
                user_orm.MessagesTable.user_id == user_id,
                user_orm.MessagesTable.receiver_id == receiver_id,
            )
        )
        .limit(50)
        .order_by(user_orm.MessagesTable.date_created)
    )
    result = await db_conn.execute(query)
    messages = result.scalars().all()

    if messages:
        return [
            orm_models.MessageTableModel.model_validate(message) for message in messages
        ]
    else:
        return []


async def update_messages_by_id(
    db_conn: db_dependency,
    id: uuid.UUID,
    values: message_model.UpdateMessageDTO | message_model.UpdateReadStatus,
):
    query = (
        update(user_orm.MessagesTable)
        .where(user_orm.MessagesTable.id == id)
        .values(**values.model_dump(exclude_unset=True))
        .returning(user_orm.MessagesTable)
    )
    result = await db_conn.execute(query)
    updated_user = result.scalar_one_or_none()
    if updated_user:
        updated_user = orm_models.MessageTableModel.model_validate(updated_user)
        await db_conn.commit()
        return updated_user
    else:
        raise error.NotFoundError


async def delete_message_by_id(db_conn: db_dependency, id: uuid.UUID):
    query = delete(user_orm.MessagesTable).where(user_orm.MessagesTable.id == id)
    result = await db_conn.execute(query)
    user = result.scalar_one_or_none()
    if user:
        await db_conn.commit()
        return None
    else:
        raise error.NotFoundError
