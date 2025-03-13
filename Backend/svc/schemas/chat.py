from pydantic import BaseModel


class SendMessage(BaseModel):
    bot_id: int
    message: str
