from pydantic import BaseModel


class CreateBot(BaseModel):
    name: str
