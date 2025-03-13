import re
import uuid

from fastapi import APIRouter, status, Depends, Request
from fastapi.exceptions import HTTPException
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse

from svc import settings
from svc.db.psql.session import get_sql_db
from svc.db.psql.models import User, Account, Bot
from svc.schemas.user import SignUp, SignIn, CreateUser, AddBotsToUser
from svc.utils.password import get_password_hash, verify_password
from svc.utils.jwt import create_access_token, verify_headers
from svc.utils.miscellaneous import (
    convert_to_lowercase_without_spaces,
    create_account_vector_db
)

user_routes = APIRouter()


@user_routes.post("/sign-up")
async def signup(payload: SignUp, sql_db=Depends(get_sql_db)):
    try:
        striped_name = convert_to_lowercase_without_spaces(payload.account_name)
        special_characters = re.compile(r'[^a-zA-Z0-9\s]')
        if special_characters.search(striped_name) is not None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Special Character is not allowed in tenant name",
            )
        if sql_db.query(Account).filter(Account.striped_name == striped_name).first():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Account with {payload.account_name} already exists",
            )

        if sql_db.query(User).filter(User.email == payload.email).first():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered",
            )

        create_account_vector_db(striped_name)

        account = Account(
            name=payload.account_name,
            striped_name=striped_name,
            api_key=uuid.uuid4().__str__()
        )

        sql_db.add(account)
        sql_db.flush()
        user = User(
            email=payload.email,
            account_id=account.id,
            is_admin=True,
        )
        sql_db.add(user)
        sql_db.commit()
        sql_db.refresh(user)
        sql_db.refresh(account)
        return JSONResponse(
            content=jsonable_encoder(
                dict(api_key=account.api_key, user_id=user.id)
            )
        )
    except Exception as exc:
        raise exc


# @user_routes.post("/sign-in")
# async def signin(payload: SignIn, sql_db=Depends(get_sql_db)):
#     try:
#         user = sql_db.query(User).filter(User.email == payload.email).first()
#         if user is not None:
#             if verify_password(payload.password, user.password):
#                 return JSONResponse(
#                     content=jsonable_encoder(
#                         dict(token=create_access_token(user=user, account=user.account))
#                     )
#                 )
#             raise HTTPException(
#                 status_code=status.HTTP_401_UNAUTHORIZED, detail="Password is incorrect"
#             )
#         raise HTTPException(
#             status_code=status.HTTP_400_BAD_REQUEST,
#             detail="Account does not exists with this email address",
#         )
#     except Exception as exc:
#         raise exc


@user_routes.post("/create-user", dependencies=[Depends(verify_headers)])
async def create_user(
    payload: CreateUser, request: Request, sql_db=Depends(get_sql_db)
):
    try:
        token_payload = await verify_headers(request)
        if token_payload["user"]["is_admin"]:
            if sql_db.query(User).filter(User.email == payload.email).first():
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"User with {payload.email} already exists",
                )
            sql_db.add(
                User(
                    email=payload.email,
                    account_id=token_payload["user"]["account_id"],
                    is_admin=False,
                )
            )
            sql_db.commit()
            return {"detail": "User added successfully"}
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="You are not authorize to perform this action",
        )
    except Exception as exc:
        raise exc


@user_routes.get("/users", dependencies=[Depends(verify_headers)])
async def get_users(request: Request, sql_db=Depends(get_sql_db)):
    try:
        token_payload = await verify_headers(request)
        if token_payload["user"]["is_admin"]:
            users = [
                user.to_dict()
                for user in sql_db.query(User)
                .filter(User.account_id == token_payload["account"]["id"])
                .all()
            ]
            return JSONResponse(content=jsonable_encoder(users))
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="You are not authorize to perform this action",
        )
    except Exception as exc:
        raise exc


@user_routes.get("/user-detail/{user_id}", dependencies=[Depends(verify_headers)])
async def get_user_detail(user_id: int, request: Request, sql_db=Depends(get_sql_db)):
    try:
        token_payload = await verify_headers(request)
        if token_payload["user"]["is_admin"] or str(token_payload["user"]["id"]) == str(
            user_id
        ):
            user = (
                sql_db.query(User)
                .filter(User.id == user_id)
                .filter(User.account_id == token_payload["account"]["id"])
                .first()
            )
            if user is not None:
                user_dict = user.to_dict()
                return JSONResponse(content=jsonable_encoder(user_dict))
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found",
            )
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="You are not authorize to perform this action",
        )
    except Exception as exc:
        raise exc


@user_routes.delete(
    "/delete-user/{user_id}", dependencies=[Depends(verify_headers)]
)
async def delete_user(user_id: int, request: Request, sql_db=Depends(get_sql_db)):
    try:
        token_payload = await verify_headers(request)
        if token_payload["user"]["is_admin"]:
            user_to_delete = (
                sql_db.query(User)
                .filter(User.id == user_id)
                .filter(User.account_id == token_payload["account"]["id"])
                .first()
            )
            if user_to_delete is not None:
                if user_to_delete.is_admin:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail="Admin user can not deleted",
                    )
                sql_db.delete(user_to_delete)
                sql_db.commit()
                return {"detail": "User deleted successfully"}
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found",
            )
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="You are not authorize to perform this action",
        )
    except Exception as exc:
        raise exc


@user_routes.put("/update-user-bots", dependencies=[Depends(verify_headers)])
async def update_user_bots(
    payload: AddBotsToUser, request: Request, sql_db=Depends(get_sql_db)
):
    try:
        token_payload = await verify_headers(request)
        if token_payload["user"]["is_admin"]:
            user = (
                sql_db.query(User)
                .filter(User.id == payload.user_id)
                .filter(User.account_id == token_payload["account"]["id"])
                .first()
            )
            if user is not None:
                user.bots = []
                bots = (
                    sql_db.query(Bot)
                    .filter(Bot.id.in_(payload.bot_ids))
                    .filter(Bot.account_id == token_payload["account"]["id"])
                    .all()
                )
                user.bots.extend(bots)
                sql_db.commit()
                return {"detail": "User's bots has been updated successfully"}
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found",
            )
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="You are not authorize to perform this action",
        )
    except Exception as exc:
        raise exc
