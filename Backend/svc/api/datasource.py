from datetime import datetime
from fastapi import APIRouter, status, Depends, Request, UploadFile, Form, File
from fastapi.exceptions import HTTPException
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse

from svc.db.psql.session import get_sql_db
from svc.db.psql.models import DataSource, Bot
from svc.utils.jwt import verify_headers
from svc.settings import blob_service_client, CONTAINER_NAME
from svc.celery import celery_app

datasource_route = APIRouter()


@datasource_route.post("/create-data-source")
async def create_data_source(
    request: Request,
    bot_id: int = Form(...),
    file: UploadFile = File(...),
    sql_db=Depends(get_sql_db),
):
    try:
        token_payload = await verify_headers(request)
        if not token_payload["user"]["is_admin"]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="You are not authorize to perform this action",
            )
        bot = sql_db.query(Bot).filter(Bot.id == bot_id).first()
        if bot is None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid Bot id",
            )

        blob_client = blob_service_client.get_blob_client(
            container=CONTAINER_NAME, blob=file.filename
        )
        blob_client.upload_blob(file.file.read(), overwrite=True)

        new_data_source = DataSource(
            bot_id=bot_id,
            filename=file.filename,
            content_type=file.content_type,
            file_url=blob_client.url,
            uploaded_at=datetime.now(),
        )
        sql_db.add(new_data_source)
        sql_db.commit()
        sql_db.refresh(new_data_source)
        result = celery_app.send_task(
            "svc.celery.tasks.llama_task.insert_index_to_vector_db",
            args=(bot.account.striped_name, bot.striped_name, new_data_source.id),
        )
        print(result)
        return {"filename": new_data_source.filename, "url": new_data_source.file_url}
    except Exception as exc:
        raise exc


@datasource_route.get(
    "/data-sources/{bot_id}", dependencies=[Depends(verify_headers)]
)
async def get_data_sources(bot_id, request: Request, sql_db=Depends(get_sql_db)):
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
                data_sources = [
                    ds.to_dict()
                    for ds in sql_db.query(DataSource).filter(
                        DataSource.bot_id == bot_id
                    )
                ]
                return JSONResponse(content=jsonable_encoder(data_sources))
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


@datasource_route.delete(
    "/data-source/{data_source_id}", dependencies=[Depends(verify_headers)]
)
async def delete_datasource(
    data_source_id: int, request: Request, sql_db=Depends(get_sql_db)
):
    token_payload = await verify_headers(request)
    try:
        if token_payload["user"]["is_admin"]:
            data_source = (
                sql_db.query(DataSource)
                .filter(DataSource.id == data_source_id)
                .join(Bot)
                .filter(Bot.account_id == token_payload["account"]["id"])
                .first()
            )
            if data_source is not None:
                sql_db.delete(data_source)
                sql_db.commit()

                try:
                    blob_client = blob_service_client.get_blob_client(
                        container=CONTAINER_NAME, blob=data_source.filename
                    )
                    blob_client.delete_blob()
                except Exception as ex:
                    print(ex)
                    pass
                return {"detail": "Datasource deleted successfully"}
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="File not found"
            )
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="You are not authorize to perform this action",
        )
    except Exception as exc:
        raise exc
