from sqlalchemy import Column, Integer, ForeignKey, Table

from svc.db.psql.models.base import Base

user_bot_table = Table(
    "user_bot",
    Base.metadata,
    Column("user_id", Integer, ForeignKey("user.id")),
    Column("bot_id", Integer, ForeignKey("bot.id")),
)
