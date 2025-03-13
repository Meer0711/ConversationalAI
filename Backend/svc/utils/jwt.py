import jwt
from datetime import datetime, timedelta
from fastapi import Request, status
from fastapi.exceptions import HTTPException
from svc import settings
from svc.db.psql.models import User, Account
from svc.db.psql.session import get_sql_db


def create_access_token(user: User, account: Account):
    data = dict(user=user.to_dict(), account=account.to_dict())
    to_encode = data.copy()
    expire = datetime.now() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(
        to_encode, settings.SECRET_KEY, algorithm=settings.HASHING_ALGORITHM
    )
    return encoded_jwt


# async def verify_access_token(request: Request):
#     auth_header = request.headers.get("Authorization")
#     if auth_header is not None:
#         split_token = auth_header.split(" ")
#         token = split_token[1] if len(split_token) > 1 else split_token[0]
#         try:
#             decode = jwt.decode(
#                 token, settings.SECRET_KEY, algorithms=[settings.HASHING_ALGORITHM]
#             )
#             db_gen = get_sql_db()
#             db = next(db_gen)
#             try:
#                 user = db.query(User).filter(User.id == decode["user"]["id"]).first()
#                 if user is None:
#                     raise HTTPException(
#                         status_code=status.HTTP_401_UNAUTHORIZED,
#                         detail="Invalid user token",
#                     )
#             finally:
#                 next(db_gen, None)
#             return decode
#         except jwt.exceptions.PyJWTError as exc:
#             raise HTTPException(
#                 status_code=status.HTTP_401_UNAUTHORIZED, detail=exc.__str__()
#             )
#
#     raise HTTPException(
#         status_code=status.HTTP_403_FORBIDDEN, detail="Authorization header missing"
#     )


async def verify_headers(request: Request):
    api_key = request.headers.get("X-API-KEY")
    user_id = request.headers.get("USER-ID")
    if api_key and user_id:
        try:
            db_gen = get_sql_db()
            db = next(db_gen)
            try:
                account = db.query(Account).filter(Account.api_key == api_key).first()
                if account is None:
                    raise HTTPException(
                        status_code=status.HTTP_401_UNAUTHORIZED,
                        detail="Invalid API-KEY",
                    )
                user = db.query(User).filter(User.id == user_id).first()
                if user is None:
                    raise HTTPException(
                        status_code=status.HTTP_401_UNAUTHORIZED,
                        detail="Invalid USER-ID",
                    )
                if user.account_id != account.id:
                    raise HTTPException(
                        status_code=status.HTTP_401_UNAUTHORIZED,
                        detail="Invalid API-KEY for user",
                    )
                #my code
                # Create dictionaries before closing the session
                user_dict = user.to_dict()
                account_dict = account.to_dict()

            finally:
                next(db_gen, None)
            # return dict(user=user.to_dict(), account=account.to_dict())
            #mycode below
            return dict(user=user_dict, account=account_dict)
        except jwt.exceptions.PyJWTError as exc:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, detail=exc.__str__()
            )

    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN, detail="X-API-KEY OR USER-ID is missing in Authorization header"
    )
