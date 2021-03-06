from typing import List
from sqlalchemy.orm import Session
from data_base import models
from fastapi import HTTPException, status
from schemas import room_collection as room_collection_schema
from security.security import get_user, check_privilege
from crud.room import read as read_room


def read_personal(db: Session, company_id: int):
    query = db.query(models.RoomCollection).filter_by(company_id=company_id)
    return query.first()


def create(db: Session, room_collection: room_collection_schema.RoomCollectionsCreate, user_id):
    user_db = get_user(db, user_id)
    if user_db.is_staff:
        room_collection_db = models.RoomCollection(**room_collection.dict(), is_public=True)
        db.add(room_collection_db)
        try:
            db.commit()
        except Exception as e:
            db.rollback()
            raise HTTPException(status_code=400, detail=str(e.orig))
    else:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )


def create_room_collection_inventory(db: Session,
                                     room_collection_inventory: room_collection_schema.RoomCollectionsInventoryCreate,
                                     user_id):
    user_db = get_user(db, user_id)
    if user_db.is_staff:
        room_collection_db = db.query(models.RoomCollection).filter_by(
            id=room_collection_inventory.room_collection_id
        ).first()
        room_collection_db.inventories.append(
            db.query(models.Inventory).filter_by(name=room_collection_inventory.inventory_name).first()
        )
        try:
            db.commit()
        except Exception as e:
            db.rollback()
            raise HTTPException(status_code=400, detail=str(e.orig))
    else:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )


def create_personal(db: Session, room_id, company_id):
    room_collection_db = models.RoomCollection(room_id=room_id, company_id=company_id, is_public=False)
    db.add(room_collection_db)
    try:
        db.commit()
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=str(e.orig))


def read_all(db: Session, user_id):
    user_db = get_user(db, user_id)
    custom_room = get_or_create_room_collection(db, user_db.company_id)
    if not custom_room:
        custom_room = read_personal(db, user_db.company_id)
    query = db.query(models.RoomCollection).filter(models.RoomCollection.room_id != custom_room.room_id).all()
    query.append(custom_room)
    return query


def get_or_create_room_collection(db, company_id):
    room_collection_db = read_personal(db, company_id)
    if not room_collection_db:
        room_db = read_room(db, "Custom Room")
        create_personal(db, room_db.id, company_id)
    return room_collection_db


def delete_inventory(db: Session, inventory_id: int, user_id: int):
    user_db = get_user(db, user_id)
    check_privilege(db, user_db, "inventory")
    room_collection_db = read_personal(db, user_db.company_id)
    inventory_db = db.query(models.Inventory).filter_by(id=inventory_id)
    room_collection_db.inventories.remove(inventory_db.first())
    inventory_db.delete()
    try:
        db.commit()
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=str(e))


def update_many_to_many_inventory(db: Session, room_collection_id: int, inventory: List[int], user_id):
    user_db = get_user(db, user_id)
    if user_db.is_staff:
        room_collection = db.query(models.RoomCollection).filter_by(id=room_collection_id).first()
        room_collection.inventories.clear()
        room_collection.inventories.extend(db.query(models.Inventory).filter(models.Inventory.id.in_(inventory)))
        try:
            db.commit()
        except Exception as e:
            db.rollback()
            raise HTTPException(status_code=400, detail=str(e))
    else:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
