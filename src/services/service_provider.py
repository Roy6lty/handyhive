import uuid
from uuid import UUID

from fastapi import HTTPException, UploadFile
from src.database.handlers import service_provider_handler
from src.root.database import db_dependency
from src.database.handlers import locations_handler
from src.models import service_provider_model
from src.services import cloudinary_service
from src.custom_exceptions import error


async def create_service_provider(
    db_conn: db_dependency, values: service_provider_model.CreateService
):
    service_id = uuid.uuid4()
    created_service_provider = await service_provider_handler.create_service_provider(
        service_id=service_id, db_conn=db_conn, services=values
    )
    if values.address:
        default_address = None
        for address in values.address:
            if address.default:
                default_address = service_provider_model.Coordinates(
                    longitude=address.longitude, latitude=address.latitude
                )
        if not default_address:
            raise HTTPException(status_code=400, detail="No default address")

        location = service_provider_model.CreateLocation(
            coordinates=default_address, service_provider_id=service_id
        )
        await locations_handler.create_service_provider_location(
            db_conn=db_conn, services=location
        )

    return created_service_provider


async def search_service_providers_by_location_and_category(
    db_conn: db_dependency, search_query: service_provider_model.SearchServices
):
    service_providers = await locations_handler.search_service_providers_by_radius(
        db_conn=db_conn, search_query=search_query
    )

    return service_providers


async def update_catalogue_picture(
    db_conn: db_dependency, service_id: UUID, catalogue_pic: list[UploadFile]
):
    new_images = []
    for pic in catalogue_pic:
        uploaded_profile = await cloudinary_service.upload_single_file(pic)
        if uploaded_profile:
            new_images.append(uploaded_profile)

    try:
        service = await service_provider_handler.get_service_provider_by_id(
            db_conn=db_conn,
            service_provider_id=service_id,
        )

        if service is None:
            raise HTTPException(status_code=404, detail="user not found")
        print(service.catalogue_pic)

        if service.catalogue_pic:
            service.catalogue_pic.extend(new_images)
        else:
            service.catalogue_pic = new_images
        await service_provider_handler.upload_service_image_by_id(
            db_conn=db_conn, service_id=service_id, image_url=service.catalogue_pic
        )

        return service_provider_model.ServiceResponse.model_validate(service)

    except error.NotFoundError:
        raise HTTPException(status_code=404, detail="user not found")


async def get_service_provider_by_id(db_conn: db_dependency, service_provider_id: UUID):
    service_provider = await service_provider_handler.get_service_by_id(
        db_conn=db_conn, service_id=service_provider_id
    )
    return service_provider_model.ServiceResponse.model_validate(service_provider)


async def update_service_provider_by_id(
    db_conn: db_dependency,
    service_provider_id: UUID,
    values: service_provider_model.UpdateServices,
):
    updated_service_provider = await service_provider_handler.update_service_by_id(
        db_conn=db_conn, service_id=service_provider_id, values=values
    )
    return updated_service_provider


async def delete_service_provider_by_id(
    db_conn: db_dependency,
    service_provider_id: UUID,
):
    updated_service_provider = await service_provider_handler.delete_service_by_id(
        db_conn=db_conn, service_id=service_provider_id
    )
    return None
