from sqlalchemy import Column, Integer, String, ForeignKey, Boolean
from sqlalchemy.orm import relationship

from svc.db.psql.models import Base
from svc.db.psql.models.m2m import user_bot_table


class User(Base):
    __tablename__ = "user"
    id = Column(Integer, primary_key=True)
    email = Column(String, unique=True)
    account_id = Column(Integer, ForeignKey("account.id"))
    is_admin = Column(Boolean, default=False)
    account = relationship("Account", back_populates="users", )
    bots = relationship("Bot", secondary=user_bot_table, back_populates="users")

    def to_dict(self):
        return dict(
            id=self.id,
            email=self.email,
            account_id=self.account_id,
            account_name=self.account.name,
            is_admin=self.is_admin,
            bots=[bot.to_dict() for bot in self.bots]
        )
