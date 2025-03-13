import pathlib
from multiprocessing.managers import BaseManager

from decouple import config  # NOQA
from azure.storage.blob import BlobServiceClient

ACCESS_TOKEN_EXPIRE_MINUTES = 240
SECRET_KEY = "rjO3KBCrHZr1MzNr42yxaaI9ARV57QgX"  # NOQA
HASHING_ALGORITHM = "HS256"
USER_DEFAULT_PASSWORD = "NewUser@1234"

# ################# POSTGRES DB ####################
POSTGRES_USER = config("POSTGRES_USER", default="postgres")
POSTGRES_PASSWORD = config("POSTGRES_PASSWORD", default="root")
POSTGRES_HOST = config("POSTGRES_HOST", default="pgvector")
POSTGRES_PORT = config("POSTGRES_PORT", default=5432)
POSTGRES_DB_NAME = config("POSTGRES_DB_NAME", default="MasterDB")
SQLALCHEMY_DATABASE_URL = (
    f"postgresql://{POSTGRES_USER}:"
    f"{POSTGRES_PASSWORD}@{POSTGRES_HOST}:"
    f"{POSTGRES_PORT}/{POSTGRES_DB_NAME}"
)
# ################ CELERY #############
REDIS_HOST = config("REDIS_URL", default="redis://redis")
REDIS_PORT = config("REDIS_PORT", default=6379, cast=int)
REDIS_BROKER_URL = f"{REDIS_HOST}:{REDIS_PORT}/0"
REDIS_RESULT_BACKEND = f"{REDIS_HOST}:{REDIS_PORT}/1"

# ################# MONGO DB ####################
MONGO_CLIENT_URL = config("MONGO_CLIENT_URL", default="mongodb://mongo:27017/")
# APP_DB_NAME = config("DB_NAME", default="ConversationalAI")

# ################### VECTOR DB ###################
# AZURE_ACCOUNT_NAME = config("AZURE_ACCOUNT_NAME", default="blobconversationalai")
# AZURE_ACCOUNT_KEY = config(
#     "AZURE_ACCOUNT_KEY",
#     default="ghwcWFRDVH1Rqjw7X5KZ4pYHLuxEid2L+lf9XXygQIRzh+gQMhG/0lRwAyjrV+GaDDYTVSHyfZMx+AStZgY2lg==",
# )
# AZURE_CONNECTION_STR = config(
#     "AZURE_CONNECTION_STR",
#     default="DefaultEndpointsProtocol=https;AccountName=blobconversationalai;"
#             "AccountKey=dG5AwuS9aobKjaSJTOdYId+tS8h3ht3eiiCe6YHTR2fOCaxcSVlj5KbXumDo7s"
#             "TadmauFRtKD/Ql+AStLwxZSg==;EndpointSuffix=core.windows.net",
# )
# CONTAINER_NAME = config("CONTAINER_NAME", default="ai-datasource")
AZURE_ACCOUNT_NAME = config("AZURE_ACCOUNT_NAME", default="conversationalai")
AZURE_ACCOUNT_KEY = config(
    "AZURE_ACCOUNT_KEY",
    default="36Fa5iTIB2vQlWHXUFel8uhraxr5WXPzwMdy9iNHYIb+UhtyBZTRo8usN+HPn1yiln8jJ3wrmPus+AStD3VyAQ==",
)
print(AZURE_ACCOUNT_NAME)
AZURE_CONNECTION_STR = config(
    "AZURE_CONNECTION_STR",
    default="DefaultEndpointsProtocol=https;AccountName=conversationalai;"
            "AccountKey=36Fa5iTIB2vQlWHXUFel8uhraxr5WXPzwMdy9iNHYIb+UhtyBZTRo8usN+HPn1yiln"
            "8jJ3wrmPus+AStD3VyAQ==;EndpointSuffix=core.windows.net",
)
CONTAINER_NAME = config("CONTAINER_NAME", default="conversationai-container")
print(CONTAINER_NAME)
AZURE_OPENAI_KEY = config(
    "AZURE_OPENAI_KEY", default="299f7532d97b43b089f31235934d61ab"
)
AZURE_OPENAI_ENDPOINT = config(
    "AZURE_OPENAI_ENDPOINT", default="https://bc-api-management-uksouth.azure-api.net"
)
AZURE_API_VERSION = config("AZURE_API_VERSION", default="2023-12-01-preview")

blob_service_client = BlobServiceClient.from_connection_string(AZURE_CONNECTION_STR)


BASE_DIR = pathlib.Path(__file__).parents[1]
