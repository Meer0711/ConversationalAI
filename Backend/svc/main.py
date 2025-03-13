import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from svc.api.user import user_routes
from svc.api.bot import bot_routes
from svc.api.chat import chat_routes
from svc.api.datasource import datasource_route

app = FastAPI(title="ai-svc")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/", name="Index")
async def index():
    return "AI Service is live"


app.include_router(user_routes, prefix="/api/v1", tags=["User"])
app.include_router(bot_routes, prefix="/api/v1", tags=["Bot"])
app.include_router(datasource_route, prefix="/api/v1", tags=["DataSource"])
app.include_router(chat_routes, prefix="/api/v1", tags=["Chat"])


if __name__ == "__main__":
    uvicorn.run("svc.main:svc", reload=True)
