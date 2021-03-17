from sqlalchemy.orm import Session

from . import sql_models, schema


def get_items(db: Session, skip: int = 0, limit: int = 100):
    return db.query(sql_models.Item).offset(skip).limit(limit).all()


def create_user_item(db: Session, item: schema.ItemCreate, user_id: int) -> schema.Item:
    db_item = sql_models.Item(**item.dict(), owner_id=user_id)
    db.add(db_item)
    db.commit()
    db.refresh(db_item)
    return db_item
