import uuid
from uuid import UUID
from src.root.database import db_dependency
from src.models import service_provider_model
from src.database.orms import user_orm
from sqlalchemy import select, update, delete
from src.custom_exceptions import error
from src.models import orm_models
from geoalchemy2.shape import from_shape
from shapely.geometry import Point


async def create_service_provider_location(
    db_conn: db_dependency, services: service_provider_model.CreateLocation
):
    new_service = user_orm.LocationTable(
        id=uuid.uuid4(),
        service_provider_id=services.service_provider_id,
        coordinates=from_shape(
            Point(services.coordinates.longitude, services.coordinates.latitude),
            srid=4326,
        ),
        longitude=services.coordinates.longitude,
        latitude=services.coordinates.latitude,
    )
    db_conn.add(new_service)
    await db_conn.commit()
    await db_conn.refresh(new_service)

    return orm_models.LocationTableModel.model_validate(new_service)


async def search_service_providers_by_radius(
    db_conn: db_dependency,
    search_query: service_provider_model.SearchServices,
    search_radius: int = 50000,
):
    # First query: by location and category
    query = (
        select(user_orm.ServiceProviderTable)
        .join(
            user_orm.LocationTable,
            user_orm.ServiceProviderTable.id
            == user_orm.LocationTable.service_provider_id,
        )
        .where(
            user_orm.LocationTable.coordinates.ST_DWithin(
                from_shape(
                    Point(
                        search_query.coordinates.longitude,
                        search_query.coordinates.latitude,
                    ),
                    srid=4326,
                ),
                search_radius,
            ),
            user_orm.ServiceProviderTable.category.overlap(search_query.category),
        )
    )

    result = await db_conn.execute(query)
    service_providers = result.scalars().all()

    if service_providers:
        for provider in service_providers:
            print(provider.address)
        return [
            orm_models.ServiceProviderTableModel.model_validate(provider)
            for provider in service_providers
        ]

    # Second query: fallback by category only
    query = select(user_orm.ServiceProviderTable).where(
        user_orm.ServiceProviderTable.category.overlap(search_query.category)
    )
    result = await db_conn.execute(query)
    service_providers = result.scalars().all()

    if service_providers:
        return [
            orm_models.ServiceProviderTableModel.model_validate(provider)
            for provider in service_providers
        ]

    # Third query: fallback by location only
    query = (
        select(user_orm.ServiceProviderTable)
        .join(
            user_orm.LocationTable,
            user_orm.ServiceProviderTable.id
            == user_orm.LocationTable.service_provider_id,
        )
        .where(
            user_orm.LocationTable.coordinates.ST_DWithin(
                from_shape(
                    Point(
                        search_query.coordinates.longitude,
                        search_query.coordinates.latitude,
                    ),
                    srid=4326,
                ),
                search_radius,
            )
        )
    )
    result = await db_conn.execute(query)
    service_providers = result.scalars().all()

    return [
        orm_models.ServiceProviderTableModel.model_validate(provider)
        for provider in service_providers
    ]


async def update_service_location_id(
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
    db_conn: db_dependency, service_id: UUID, image_url: str
):
    query = (
        update(user_orm.ServiceProviderTable)
        .where(user_orm.ServiceProviderTable.id == service_id)
        .values(image_url=image_url)
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
