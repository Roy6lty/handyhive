from uuid import UUID

from fastapi import HTTPException, UploadFile
from src.root.database import db_dependency
from src.database.handlers import services_handler, locations_handler
from src.models import services_model
from src.services import cloudinary_service
from src.custom_exceptions import error


async def create_service_provider(
    db_conn: db_dependency, values: services_model.CreateService
):
    created_service_provider = await services_handler.create_service_provider(
        db_conn=db_conn, services=values
    )
    if values.location:
        location = services_model.CreateLocation(
            coordinates=values.location, service_provider_id=created_service_provider.id
        )
        await locations_handler.create_service_provider_location(
            db_conn=db_conn, services=location
        )

    return created_service_provider


async def search_service_providers_by_location_and_category(
    db_conn: db_dependency, search_query: services_model.SearchServices
):
    service_providers = await locations_handler.search_service_providers_by_radius(
        db_conn=db_conn, search_query=search_query
    )

    return service_providers


async def update_catalogue_picture(
    db_conn: db_dependency, service_id: UUID, catalogue_pic: list[UploadFile]
):

    new_images = []
    # upload image
    for pic in catalogue_pic:
        uploaded_profile = await cloudinary_service.upload_single_file(pic)
        new_images.append(uploaded_profile)

    try:
        service = await services_handler.get_service_by_id(
            db_conn=db_conn,
            service_id=service_id,
        )
        if service.catalogue_pic is None:
            updated_catalogue = new_images
        else:
            updated_catalogue = service.catalogue_pic
            updated_catalogue.extend(new_images)

        await services_handler.upload_service_image_by_id(
            db_conn=db_conn, service_id=service_id, image_url=updated_catalogue
        )
        return services_model.ServiceResponse.model_validate(service)
    except error.NotFoundError:
        raise HTTPException(status_code=404, detail="user not found")


async def get_service_provider_by_id(db_conn: db_dependency, service_provider_id: UUID):
    service_provider = await services_handler.get_service_by_id(
        db_conn=db_conn, service_id=service_provider_id
    )
    return services_model.ServiceResponse.model_validate(service_provider)


async def update_service_provider_by_id(
    db_conn: db_dependency,
    service_provider_id: UUID,
    values: services_model.UpdateServices,
):
    updated_service_provider = await services_handler.update_service_by_id(
        db_conn=db_conn, service_id=service_provider_id, values=values
    )
    return updated_service_provider


async def delete_service_provider_by_id(
    db_conn: db_dependency,
    service_provider_id: UUID,
):
    updated_service_provider = await services_handler.delete_service_by_id(
        db_conn=db_conn, service_id=service_provider_id
    )
    return None
