from fastapi import APIRouter
from src.routes.actors.providers.service_provider_route import (
    router as service_provider_router,
)
from src.routes.profile_route import router as profile_route
from src.routes.authentication import router as authentication_router
from src.routes.services_route import router as service_router
from src.routes.message_route import router as message_router
from src.routes.actors.customers.booking_route import router as customer_router
from src.routes.actors.customers.customer_invoice_route import router as invoice_router


api_router = APIRouter()

api_router.include_router(router=authentication_router)
api_router.include_router(router=service_router)
api_router.include_router(router=service_provider_router)
api_router.include_router(router=profile_route)
api_router.include_router(router=message_router)
api_router.include_router(router=customer_router)
api_router.include_router(router=invoice_router)
