from sqlalchemy.orm import Session
from data_base import models
from fastapi import HTTPException
from schemas import street as street_schema

def read(db: Session, id: int):
    query = db.query(models.Street).filter(models.Street.id == id)
    return query.first()

def create(db: Session, street: street_schema.StreetCreate):
    street_db = models.Street(**street.dict())
    db.add(street_db)
    try:
        db.commit()
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e.orig))

def get_or_create(db: Session, street_name: str):
    street_db = models.Street(street_name=street_name)
    db.add(street_db)
    try:
        db.commit()
    except Exception:
        db.rollback()
        street_db = db.query(models.Street).filter(models.Street.street_name == street_name).first()
    return street_db

def read_all(db: Session):
    query = db.query(models.Street)
    return query.all()
