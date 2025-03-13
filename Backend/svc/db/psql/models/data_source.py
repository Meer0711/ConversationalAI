from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Boolean
from sqlalchemy.orm import relationship

from svc.db.psql.models.base import Base
from svc.utils.miscellaneous import get_blob_url_with_sas


class DataSource(Base):
    __tablename__ = "datasource"
    id = Column(Integer, primary_key=True)
    bot_id = Column(Integer, ForeignKey("bot.id"))
    filename = Column(String)
    content_type = Column(String)
    file_url = Column(String)
    uploaded_at = Column(DateTime)
    is_index_created = Column(Boolean, default=False)
    bot = relationship("Bot", back_populates="data_sources")

    def to_dict(self):
        return dict(
            id=self.id,
            bot_id=self.bot_id,
            filename=self.filename,
            file_url=self.file_url,
            uploaded_at=self.uploaded_at,
            is_index_created=self.is_index_created,
            download_url=get_blob_url_with_sas(self.filename)
        )
