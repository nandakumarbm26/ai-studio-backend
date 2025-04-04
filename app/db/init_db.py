from app.db.base import Base
from app.db.session import engine
import app.models.item  # import all models

Base.metadata.create_all(bind=engine)