import select
from typing import Any
import uuid
from src.database.orms import user_orm
from src.root.database import db_dependency
from sqlalchemy import select, delete, and_
from src.custom_exceptions import error
from src.models import orm_models
from src.models import notifications


async def create_notification(
    db_conn: db_dependency,
    notification: notifications.CreateNotifications,
) -> orm_models.NotificationsTableModel:
    new_message = user_orm.NotificationsTable(
        id=uuid.uuid4(), **notification.model_dump()
    )
    db_conn.add(new_message)
    await db_conn.commit()
    await db_conn.refresh(new_message)

    return orm_models.NotificationsTableModel.model_validate(new_message)


async def get_unread_notifications_by_user_id(
    db_conn: db_dependency, user_id: uuid.UUID
) -> list[orm_models.NotificationsTableModel] | list[Any]:
    query = select(user_orm.NotificationsTable).where(
        and_(
            user_orm.NotificationsTable.user_id == user_id,
            user_orm.NotificationsTable.read == False,
        )
    )
    result = await db_conn.execute(query)
    messages = result.scalars().all()

    if len(messages) > 0:
        return [
            orm_models.NotificationsTableModel.model_validate(message)
            for message in messages
        ]
    else:
        return []


async def delete_notifications_by_id(db_conn: db_dependency, id: uuid.UUID):
    query = delete(user_orm.NotificationsTable).where(
        user_orm.NotificationsTable.id == id
    )
    result = await db_conn.execute(query)
    user = result.scalar_one_or_none()
    if user:
        await db_conn.commit()
        return None
    else:
        raise error.NotFoundError
