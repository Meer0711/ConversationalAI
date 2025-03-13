from uuid import uuid4

from sqlalchemy import Column, Integer, String, UUID, func
from sqlalchemy.orm import relationship

from svc.db.psql.models.base import Base


class Account(Base):
    __tablename__ = "account"
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    striped_name = Column(String, unique=True)
    api_key = Column(UUID)
    users = relationship("User", back_populates="account", lazy="selectin")
    bots = relationship("Bot", back_populates="account")

    def to_dict(self):
        return dict(id=self.id, name=self.name, striped_name=self.striped_name)
