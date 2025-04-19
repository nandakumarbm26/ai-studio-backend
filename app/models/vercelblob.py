from sqlalchemy import Column, String, Integer
from app.db.base import Base


class VercelBlobMetaData(Base):
    __tablename__ = "vercel_blob_metadata"

    id = Column(String, primary_key=True, index=True)
    contentDisposition = Column(String, nullable=False)
    contentType = Column(String, nullable=False)
    downloadUrl = Column(String, nullable=False)
    pathname = Column(String, nullable=False)
    url = Column(String, nullable=False)
    userid = Column(Integer, nullable=True)


