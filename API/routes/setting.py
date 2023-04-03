# Description: API calls to CRUD operations for the settings table.

from database.config import get_db
from fastapi import APIRouter, Depends, HTTPException
from models.setting import Settings
from schemas.setting import BaseSetting, Setting
from sqlalchemy.orm import Session

# Create the settings router
settings = APIRouter()

# Create a new setting
@settings.post("/settings", response_model=Setting)
def create_setting(setting: BaseSetting, db: Session = Depends(get_db)):

    # Check if the setting already exists (by key)
    if db.query(Settings).filter(Settings.key == setting.key).first():
        raise HTTPException(
            status_code=400,
            detail=f"Setting already exists by key ({setting.key})",
        )

    # Create a new setting model with the data from the request
    db_setting = Settings(
        key=setting.key,
        value=setting.value,
        description=setting.description,
    )

    # Add the setting to the database
    db.add(db_setting)
    db.commit()

    # Return the setting created
    return db_setting


# Get all the settings
@settings.get("/settings", response_model=list[Setting])
def get_settings(db: Session = Depends(get_db)):

    # Return all the settings
    return db.query(Settings).all()


# Get a setting by key
@settings.get("/settings/{key}", response_model=Setting)
def get_setting(key: str, db: Session = Depends(get_db)):

    # Return the setting by key
    return db.query(Settings).filter(Settings.key == key).first()


# Update a setting by key
@settings.put("/settings/{key}", response_model=Setting)
def update_setting(key: str, setting: Setting, db: Session = Depends(get_db)):

    # Check if the setting already exists (by key)
    db_setting = db.query(Settings).filter(Settings.key == key).first()

    if db_setting is None:
        raise HTTPException(
            status_code=404, detail=f"Setting with key: {key} not found"
        )

    # Update the setting
    for key, value in setting.dict(exclude_unset=True).items():
        setattr(db_setting, key, value)

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
