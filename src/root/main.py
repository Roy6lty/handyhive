import os
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from src.middleware import exception_middleware
from src.middleware import session_middleware

# from backend.src.middleware.ratelimiting import limiter
from src.root.database import shutdown, startup
from src.root.env_settings import env

from src.root.subrouter import api_router


@asynccontextmanager
async def app_lifespan(app: FastAPI):
    await startup()
    yield
    await shutdown()


app = FastAPI(title="Handy Hive Project", version="0.0.1", lifespan=app_lifespan)

# app.state.limiter = limiter

app.include_router(router=api_router)

origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
allowed_exceptions = (HTTPException, os)


# middleware
config = exception_middleware.ExceptionLoggingMiddlewareConfig(
    print_to_console=env.DEBUG_MODE
)
exception_middleware.add_exception_middleware(app, config=config)
session_middleware.add_session_middleware(app, secret_key=env.SECRET_KEY)
