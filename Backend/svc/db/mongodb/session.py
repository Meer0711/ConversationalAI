from contextlib import asynccontextmanager
from fastapi import Request
from motor.motor_asyncio import AsyncIOMotorClient
from svc import settings
from svc.utils.jwt import verify_headers


async def get_nosql_db(request: Request):
    token_payload = await verify_headers(request)
    db_name = token_payload["account"]["striped_name"]
    client = AsyncIOMotorClient(settings.MONGO_CLIENT_URL)
    try:
        db = client.get_database(db_name)
        yield db
    finally:
        client.close()


@asynccontextmanager
async def get_celery_nosql_db(db_name):
    client = AsyncIOMotorClient(settings.MONGO_CLIENT_URL)
    try:
        db = client.get_database(db_name)
        yield db
    finally:
        client.close()
