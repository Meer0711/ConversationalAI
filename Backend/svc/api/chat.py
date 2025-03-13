import time
from bson.objectid import ObjectId # NOQA

from fastapi import APIRouter, status, Depends, Request
from fastapi.exceptions import HTTPException

from svc.schemas.chat import SendMessage
from svc.db.psql.session import get_sql_db
from svc.db.mongodb.session import get_nosql_db
from svc.db.psql.models import Bot, user_bot_table, DataSource
from svc.utils.jwt import verify_headers
from svc.celery import celery_app

chat_routes = APIRouter()


@chat_routes.get("/bot-messages/{bot_id}", dependencies=[Depends(verify_headers)])
async def get_bot_messages(
        bot_id, request: Request, sql_db=Depends(get_sql_db), nosql_db=Depends(get_nosql_db)
):
    try:
        token_payload = await verify_headers(request)
        bot = (
            sql_db.query(Bot)
            .filter(Bot.id == bot_id)
            .filter(Bot.account_id == token_payload["account"]["id"])
            .first()
        )
        if bot is not None:
            user_bot_relation = (
                sql_db.query(user_bot_table)
                .filter(
                    user_bot_table.c.user_id == token_payload["user"]["id"],
                    user_bot_table.c.bot_id == bot_id,
                )
                .first()
            )
            if user_bot_relation:
                messages = []
                async for row in nosql_db[bot.striped_name].find(
                        {"user_id": token_payload["user"]["id"]}
                ):
                    row["_id"] = str(row["_id"])
                    messages.append(row)
                return messages
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="You are not allowed to access this bot",
            )
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Bot not found",
        )
    except Exception as exc:
        raise exc


@chat_routes.post("/send-message", dependencies=[Depends(verify_headers)])
async def send_message(
        payload: SendMessage,
        request: Request,
        sql_db=Depends(get_sql_db),
        nosql_db=Depends(get_nosql_db),
):
    try:
        token_payload = await verify_headers(request)
        bot = (
            sql_db.query(Bot)
            .filter(Bot.id == payload.bot_id)
            .filter(Bot.account_id == token_payload["account"]["id"])
            .first()
        )
        if bot is not None:
            user_bot_relation = (
                sql_db.query(user_bot_table)
                .filter(
                    user_bot_table.c.user_id == token_payload["user"]["id"],
                    user_bot_table.c.bot_id == payload.bot_id,
                )
                .first()
            )

            if user_bot_relation:
                data_sources = (
                    sql_db.query(DataSource)
                    .filter(DataSource.bot_id == payload.bot_id)
                    .filter(DataSource.is_index_created == True)  # NOQA
                    .all()
                )
                if not data_sources:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail="No datasource available for this bot, "
                               "Please Upload the datasource to start the conversation"
                    )
                await nosql_db[bot.striped_name].insert_one(
                    {
                        "bot_id": payload.bot_id,
                        "user_id": token_payload["user"]["id"],
                        "account_id": token_payload["account"]["id"],
                        "sender": token_payload["user"]["email"],
                        "class": "rightAlignment",
                        "message": payload.message,
                        "timestamp": int(time.time() * 1000)
                    }
                )

                bot_response = {
                    "bot_id": payload.bot_id,
                    "user_id": token_payload["user"]["id"],
                    "account_id": token_payload["account"]["id"],
                    "sender": bot.name,
                    "class": "leftAlignment",
                    "message": "WaitingForBotResponse",
                    "timestamp": int(time.time() * 1000)
                }
                await nosql_db[bot.striped_name].insert_one(bot_response)
                message_id = str(bot_response.pop("_id"))
                bot_response["id"] = message_id
                celery_app.send_task(
                    "svc.celery.tasks.llama_task.query_index",
                    args=(
                        bot.account.striped_name,
                        bot.striped_name,
                        message_id,
                        payload.message,
                    ),
                )
                return bot_response

            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="You are not allowed to send message to this bot",
            )
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Bot not found",
        )
    except Exception as exc:
        raise exc


@chat_routes.get(
    "/get-message/{bot_id}/{message_id}", dependencies=[Depends(verify_headers)]
)
async def get_message(
        request: Request,
        bot_id,
        message_id: str,
        sql_db=Depends(get_sql_db),
        nosql_db=Depends(get_nosql_db),
):
    try:
        token_payload = await verify_headers(request)
        bot = sql_db.query(Bot).filter(Bot.id == bot_id).first()
        if bot is not None:
            user_bot_relation = (
                sql_db.query(user_bot_table)
                .filter(
                    user_bot_table.c.user_id == token_payload["user"]["id"],
                    user_bot_table.c.bot_id == bot_id,
                )
                .first()
            )

            if user_bot_relation:
                document = await nosql_db[bot.striped_name].find_one(
                    {"_id": ObjectId(message_id)}
                )
                if document is not None:
                    document["_id"] = str(document["_id"])
                    return document
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Invalid message id",
                )
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="You are not allowed to get message",
            )
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid Bot id",
        )
    except Exception as exc:
        raise exc
