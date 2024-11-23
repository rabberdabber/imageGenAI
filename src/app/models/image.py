from datetime import datetime

from sqlalchemy import Column, DateTime, String

from ..core.db.base_class import Base


class Image(Base):
    __tablename__ = "images"

    id = Column(String(36), primary_key=True)  # UUID stored as string
    filename = Column(String, unique=True, index=True)
    original_filename = Column(String)
    file_path = Column(String)
    url = Column(String)
    content_type = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self) -> str:
        return f"<Image {self.filename}>"
