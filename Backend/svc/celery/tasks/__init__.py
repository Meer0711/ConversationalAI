from llama_index.llms.azure_openai import AzureOpenAI
from llama_index.embeddings.azure_openai import AzureOpenAIEmbedding
from llama_index.core import Settings
from svc import settings

llm = AzureOpenAI(
    model="gpt-4-32k",
    deployment_name="gpt-4-32k",
    api_key=settings.AZURE_OPENAI_KEY,
    azure_endpoint=settings.AZURE_OPENAI_ENDPOINT,
    api_version=settings.AZURE_API_VERSION,
)
embed_model = AzureOpenAIEmbedding(
    model="text-embedding-ada-002",
    deployment_name="text-embedding-ada-002",
    api_key=settings.AZURE_OPENAI_KEY,
    azure_endpoint=settings.AZURE_OPENAI_ENDPOINT,
    api_version=settings.AZURE_API_VERSION,
)
Settings.llm = llm
Settings.embed_model = embed_model
