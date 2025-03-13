from fastapi import APIRouter, status, Depends, Request
from fastapi.exceptions import HTTPException
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse

from svc.db.psql.session import get_sql_db
from svc.db.psql.models import Bot
from svc.schemas.bot import CreateBot
from svc.utils.jwt import verify_headers
from svc.utils.miscellaneous import convert_to_lowercase_without_spaces

bot_routes = APIRouter()


@bot_routes.post("/create-bot", dependencies=[Depends(verify_headers)])
async def create_bot(payload: CreateBot, request: Request, sql_db=Depends(get_sql_db)):
    try:
        token_payload = await verify_headers(request)
        striped_name = convert_to_lowercase_without_spaces(payload.name)
        if token_payload["user"]["is_admin"]:
            if sql_db.query(Bot).filter(
                Bot.account_id == token_payload["account"]["id"],
                Bot.striped_name == striped_name
            ).first():
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Bot with {payload.name} already exists",
                )
            sql_db.add(
                Bot(
                    name=payload.name,
                    striped_name=striped_name,
                    account_id=token_payload["user"]["account_id"],
                )
            )
            sql_db.commit()
            return {"detail": "Bot added successfully"}
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="You are not authorize to perform this action",
        )
    except Exception as exc:
        raise exc


@bot_routes.get("/bots", dependencies=[Depends(verify_headers)])
async def get_bots(request: Request, sql_db=Depends(get_sql_db)):
    try:
        token_payload = await verify_headers(request)
        if token_payload["user"]["is_admin"]:
            users = [
                bot.to_dict()
                for bot in sql_db.query(Bot).filter(
                    Bot.account_id == token_payload["account"]["id"]
                )
            ]
            return JSONResponse(content=jsonable_encoder(users))
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="You are not authorize to perform this action",
        )
    except Exception as exc:
        raise exc


@bot_routes.get("/bot-detail/{bot_id}", dependencies=[Depends(verify_headers)])
async def get_bot_detail(bot_id: int, request: Request, sql_db=Depends(get_sql_db)):
    try:
        token_payload = await verify_headers(request)
        if token_payload["user"]["is_admin"]:
            bot = (
                sql_db.query(Bot)
                .filter(Bot.id == bot_id)
                .filter(Bot.account_id == token_payload["account"]["id"])
                .first()
            )
            if bot is not None:
                return JSONResponse(content=jsonable_encoder(bot.to_dict()))
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Bot not found",
            )
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="You are not authorize to perform this action",
        )
    except Exception as exc:
        raise exc


@bot_routes.delete("/delete-bot/{bot_id}", dependencies=[Depends(verify_headers)])
async def delete_bot(bot_id: str, request: Request, sql_db=Depends(get_sql_db)):
    try:
        token_payload = await verify_headers(request)
        if token_payload["user"]["is_admin"]:
            bot_to_delete = (
                sql_db.query(Bot)
                .filter(Bot.id == bot_id)
                .filter(Bot.account_id == token_payload["account"]["id"])
                .first()
            )
            if bot_to_delete is not None:
                sql_db.delete(bot_to_delete)
                sql_db.commit()
                return {"detail": "Bot deleted successfully"}
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Bot not found",
            )
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="You are not authorize to perform this action",
        )
    except Exception as exc:
        raise exc
