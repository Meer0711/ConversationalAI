from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship

from svc.db.psql.models.base import Base

from svc.db.psql.models.m2m import user_bot_table


class Bot(Base):
    __tablename__ = "bot"
    id = Column(Integer, primary_key=True)
    name = Column(String)
    striped_name = Column(String)
    account_id = Column(Integer, ForeignKey("account.id"))
    account = relationship("Account", back_populates="bots")
    users = relationship("User", secondary=user_bot_table, back_populates="bots")
    data_sources = relationship(
        "DataSource", back_populates="bot", cascade="all, delete"
    )

    def to_dict(self):
        return dict(
            id=self.id, name=self.name, account_id=self.account_id,
            data_sources=[ds.to_dict() for ds in self.data_sources]
        )
