import uuid
from uuid import UUID
from src.root.database import db_dependency
from src.models import service_provider_model
from src.database.orms import user_orm
from sqlalchemy import select, update, delete
from sqlalchemy.orm import joinedload
from src.custom_exceptions import error
from src.models import orm_models


async def create_service_provider(
    service_id: uuid.UUID,
    db_conn: db_dependency,
    services: service_provider_model.CreateService,
):
    new_service = user_orm.ServiceProviderTable(
        id=service_id,
        category=list(services.services_provided.keys()),
        **services.model_dump(exclude={"category", "location"})
    )
    db_conn.add(new_service)
    await db_conn.commit()
    await db_conn.refresh(new_service)

    return orm_models.ServiceProviderTableModel.model_validate(new_service)


async def get_service_by_id(db_conn: db_dependency, service_id: UUID):
    service = (
        select(user_orm.ServiceProviderTable)
        .options(joinedload(user_orm.ServiceProviderTable.location))
        .join(user_orm.LocationTable.provider)
        .where(user_orm.ServiceProviderTable.id == service_id)
    )

    result = await db_conn.execute(service)
    found_service = result.unique().scalar_one_or_none()
    if found_service:
        found_service.location
        return orm_models.ServiceProviderTableModel.model_validate(found_service)

    else:
        raise error.NotFoundError


async def get_service_provider_by_id(
    db_conn: db_dependency, service_provider_id: uuid.UUID
):
    service_provider = select(user_orm.ServiceProviderTable).where(
        user_orm.ServiceProviderTable.id == service_provider_id
    )

    result = await db_conn.execute(service_provider)
    found_service = result.scalar_one_or_none()
    if found_service:
        return orm_models.ServiceProviderTableModel.model_validate(found_service)


async def update_service_by_id(
    db_conn: db_dependency,
    service_id: UUID,
    values: service_provider_model.UpdateServices,
):
    if values.services_provided is not None:
        values_json = values.model_dump(exclude_unset=True)
        values_json["category"] = list(values_json["services_provided"].keys())
    else:
        values_json = values.model_dump(exclude_unset=True)
    query = (
        update(user_orm.ServiceProviderTable)
        .where(user_orm.ServiceProviderTable.id == service_id)
        .values(**values_json)
        .returning(user_orm.ServiceProviderTable)
    )
    result = await db_conn.execute(query)
    updated_service = result.scalar_one_or_none()
    if updated_service:
        return orm_models.ServiceProviderTableModel.model_validate(updated_service)
    else:
        raise error.NotFoundError


async def upload_service_image_by_id(
    db_conn: db_dependency, service_id: UUID, image_url: list[str]
):
    query = (
        update(user_orm.ServiceProviderTable)
        .where(user_orm.ServiceProviderTable.id == service_id)
        .values(catalogue_pic=image_url)
        .returning(user_orm.ServiceProviderTable)
    )
    result = await db_conn.execute(query)
    updated_service = result.scalar_one_or_none()
    if updated_service:
        return orm_models.ServiceProviderTableModel.model_validate(updated_service)
    else:
        raise error.NotFoundError


async def delete_service_by_id(db_conn: db_dependency, service_id: UUID):
    query = (
        delete(user_orm.ServiceProviderTable)
        .where(user_orm.ServiceProviderTable.id == service_id)
        .returning(user_orm.ServiceProviderTable)
    )
    result = await db_conn.execute(query)
    deleted_service = result.scalar_one_or_none()
    if deleted_service:
        await db_conn.commit()
        return None
    else:
        raise error.NotFoundError
