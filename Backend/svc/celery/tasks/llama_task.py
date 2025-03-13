import asyncio
from bson.objectid import ObjectId
from llama_index.readers.file import PyMuPDFReader
from llama_index.vector_stores.postgres import PGVectorStore
from llama_index.core import VectorStoreIndex, StorageContext
from sqlalchemy import make_url

from svc import settings
from svc.celery import celery_app
from svc.utils.miscellaneous import get_file_path
from svc.db.psql.models import DataSource
from svc.db.psql.session import get_sql_db
from svc.db.mongodb.session import get_celery_nosql_db


def get_or_create_vector_store(db_name, bot_name):
    url = make_url(settings.SQLALCHEMY_DATABASE_URL)
    return PGVectorStore.from_params(
        database=db_name,
        host=url.host,
        password=url.password,
        port=url.port,
        user=url.username,
        table_name=bot_name,
        cache_ok=True
    )


@celery_app.task(
    name="svc.celery.tasks.llama_task.insert_index_to_vector_db", bind=True
)
def insert_index_to_vector_db(self, account_name, bot_name, data_source_id):
    try:
        sql_db = next(get_sql_db())
        data_source = sql_db.query(DataSource).filter(DataSource.id == data_source_id).first()
        loader = PyMuPDFReader()
        filepath = get_file_path(data_source.filename)
        documents = loader.load(file_path=filepath)
        for document in documents:
            document.text = document.text.replace("\x00", "")
        vector_store = get_or_create_vector_store(account_name, bot_name)
        storage_context = StorageContext.from_defaults(vector_store=vector_store)
        VectorStoreIndex.from_documents(
            documents, storage_context=storage_context, show_progress=True
        )
        setattr(data_source, "is_index_created", True)
        sql_db.commit()
    except Exception as exc:
        raise exc


@celery_app.task(name="svc.celery.tasks.llama_task.query_index", bind=True)
def query_index(self, account_name, bot_name, message_id, query: str):
    try:
        vector_store = get_or_create_vector_store(account_name, bot_name)
        index = VectorStoreIndex.from_vector_store(vector_store=vector_store)
        query_engine = index.as_query_engine()
        response = query_engine.query(query.strip())
        print("**********************************************************")
        print(f"Query: >> {query}")
        print(f"Response: >> {response.__str__()}")
        print("**********************************************************")

        async def run_db_operations():
            async with get_celery_nosql_db(account_name) as nosql_db:
                update_data = {"$set": {"message": response.__str__()}}
                await nosql_db[bot_name].update_one({"_id": ObjectId(message_id)}, update_data)

        asyncio.run(run_db_operations())

    except Exception as exc:
        raise exc
