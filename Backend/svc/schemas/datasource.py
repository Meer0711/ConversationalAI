from pydantic import BaseModel


class DataSourcePayload(BaseModel):
    bot_id: int
