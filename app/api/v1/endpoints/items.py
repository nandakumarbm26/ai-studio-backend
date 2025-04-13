from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.schemas.item import ItemCreate, ItemResponse
from app.crud.item import create_item, get_items
from app.db.session import get_db

router = APIRouter()
@router.post("/", response_model=ItemResponse)
def create(item: ItemCreate, db: Session = Depends(get_db)):
    return create_item(db, item)

@router.get("/", response_model=list[ItemResponse])
def read_all(db: Session = Depends(get_db)):
    return get_items(db)