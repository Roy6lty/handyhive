import select
import uuid
from src.database.orms import user_orm
from src.root.database import db_dependency
from src.models import user_model
from sqlalchemy import select, update, delete
from src.custom_exceptions import error
from src.models import orm_models
from src.models import authentication
from src.models import user_model
from src.models.token_models import Roles


async def create_user(
    db_conn: db_dependency,
    user: authentication.CreateUserSchema | authentication.OpenIDUserDataModel,
    hashed_password: str | None,
    role: str = user_model.Roles.USER,
    referral_code: str | None = None,
):
    new_user = user_orm.UserTable(
        id=uuid.uuid4(),
        role=role,
        referral_code=referral_code,
        hashed_password=hashed_password,
        **user.model_dump(exclude={"hashed_password"})
    )
    db_conn.add(new_user)
    await db_conn.commit()
    await db_conn.refresh(new_user)

    return orm_models.UserTableModel.model_validate(new_user)


async def get_user_by_id(db_conn: db_dependency, user_id: uuid.UUID):
    query = select(user_orm.UserTable).where(user_orm.UserTable.id == user_id)
    result = await db_conn.execute(query)
    user = result.scalar_one_or_none()

    if user:
        return orm_models.UserTableModel.model_validate(user)
    else:
        raise error.NotFoundError


async def get_user_by_email(db_conn: db_dependency, email: str):
    query = select(user_orm.UserTable).where(user_orm.UserTable.email == email)
    result = await db_conn.execute(query)
    user = result.scalar_one_or_none()

    if user:
        return orm_models.UserTableModel.model_validate(user)
    else:
        raise error.NotFoundError


async def update_user_by_id(
    db_conn: db_dependency,
    user_id: uuid.UUID,
    values: (
        user_model.UpdateUser | user_model.UpdateUserProfile | user_model.Update2faCode
    ),
):
    query = (
        update(user_orm.UserTable)
        .where(user_orm.UserTable.id == user_id)
        .values(**values.model_dump(exclude_unset=True))
        .returning(user_orm.UserTable)
    )
    result = await db_conn.execute(query)
    updated_user = result.scalar_one_or_none()
    if updated_user:
        updated_user = orm_models.UserTableModel.model_validate(updated_user)
        await db_conn.commit()
        return updated_user
    else:
        raise error.NotFoundError


async def delete_user_by_id(db_conn: db_dependency, user_id: uuid.UUID):
    query = delete(user_orm.UserTable).where(user_orm.UserTable.id == user_id)
    result = await db_conn.execute(query)
    user = result.scalar_one_or_none()
    if user:
        await db_conn.commit()
        return None
    else:
        raise error.NotFoundError
