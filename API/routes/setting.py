# Description: API calls to CRUD operations for the settings table.

from database.config import Base, engine, get_db
from fastapi import APIRouter, Depends, HTTPException
from models.setting import Settings
from schemas.setting import Setting
from sqlalchemy.orm import Session

# Create the settings router
settings = APIRouter()

# Create the databases tables
Base.metadata.create_all(bind=engine)

# Create a new setting
@settings.post("/settings", response_model=Setting)
def create_setting(setting: Setting, db: Session = Depends(get_db)):

    db_setting = Settings(
        key=setting.key,
        value=setting.value,
        description=setting.description,
    )

    db.add(db_setting)
    db.commit()

    return db_setting


# Get all the settings
@settings.get("/settings", response_model=list[Setting])
def get_settings(db: Session = Depends(get_db)):
    return db.query(Settings).all()


# Get a setting by key
@settings.get("/settings/{key}", response_model=Setting)
def get_setting(key: str, db: Session = Depends(get_db)):
    return db.query(Settings).filter(Settings.key == key).first()


# Update a setting by key
@settings.put("/settings/{key}", response_model=Setting)
def update_setting(key: str, setting: Setting, db: Session = Depends(get_db)):

    db_setting = db.query(Settings).filter(Settings.key == key).first()

    if db_setting is None:
        raise HTTPException(
            status_code=404, detail=f"Setting with key: {key} not found"
        )

    db_setting.key = setting.key
    db_setting.value = setting.value
    db_setting.description = setting.description

    db.add(db_setting)
    db.commit()

    return db_setting


# Delete a setting by key
@settings.delete("/settings/{key}", response_model=Setting)
def delete_setting(key: str, db: Session = Depends(get_db)):

    db_setting = db.query(Settings).filter(Settings.key == key).first()

    if db_setting is None:
        raise HTTPException(
            status_code=404, detail=f"Setting with key: {key} not found"
        )

    db.delete(db_setting)
    db.commit()

    return db_setting
