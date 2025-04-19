
import strawberry
from typing import List, Optional
from uuid import uuid4
from sqlalchemy.orm import Session

from app.models.vercelblob import VercelBlobMetaData as FileModel
from app.db.session import get_db


@strawberry.type
class FileType():
    id: str
    contentDisposition: str
    contentType: str
    downloadUrl: str
    pathname: str
    url: str


@strawberry.input
class FileInput:
    contentDisposition: str
    contentType: str
    downloadUrl: str
    pathname: str
    url: str


@strawberry.type
class VercelBlobMetaDataMutation:

    @strawberry.mutation
    def create_file(self, input: FileInput) -> FileType:
        db: Session = next(get_db())
        file = FileModel(id=str(uuid4()), **input.__dict__)
        db.add(file)
        db.commit()
        db.refresh(file)
        return file

    @strawberry.mutation
    def update_file(self, id: str, input: FileInput) -> Optional[FileType]:
        db: Session = next(get_db())
        file = db.query(FileModel).filter(FileModel.id == id).first()
        if not file:
            return None
        for key, value in input.__dict__.items():
            setattr(file, key, value)
        db.commit()
        db.refresh(file)
        return file

    @strawberry.mutation
    def delete_file(self, id: str) -> bool:
        db: Session = next(get_db())
        file = db.query(FileModel).filter(FileModel.id == id).first()
        if file:
            db.delete(file)
            db.commit()
            return True
        return False


@strawberry.type
class VercelBlobMetaDataQuery:

    @strawberry.field
    def all_files(self) -> List[FileType]:
        db: Session = next(get_db())
        return db.query(FileModel).all()

    @strawberry.field
    def vercel_blob_metadata(self, id: str) -> Optional[FileType]:
        db: Session = next(get_db())
        return db.query(FileModel).filter(FileModel.id == id).first()


