# Description: API calls to CRUD operations for the settings table.

from database.config import get_db
from fastapi import APIRouter, Depends, HTTPException, status
from models.setting import Settings
from schemas.setting import BaseSetting, Setting
from sqlalchemy.orm import Session

# Create the settings router
settings = APIRouter()

# Create a new setting
@settings.post(
    "/settings",
    response_model=Setting,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new setting",
)
def create_setting(setting: BaseSetting, db: Session = Depends(get_db)):

    """
    Create a new setting in the database with the data from the request.

    **-key**: Identifier for the setting.
    **-value**: Value for the setting.
    **-description**: Description for the setting (optional).

    **Raises:** HTTPException: 400 - Setting already exists by key.

    Returns:
        _type_: _description_
    """

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
@settings.get(
    "/settings",
    response_model=list[Setting],
    summary="Get all the settings",
    status_code=status.HTTP_200_OK,
)
def get_settings(db: Session = Depends(get_db)):

    """
    Get all the settings of the system from the database.

    Returns: List of settings.
    """

    # Return all the settings
    return db.query(Settings).all()


# Get a setting by key
@settings.get(
    "/settings/{key}",
    response_model=Setting,
    status_code=status.HTTP_200_OK,
    summary="Get a setting by key",
)
def get_setting(key: str, db: Session = Depends(get_db)):

    """
    Get a setting of the system by key from the database.

    **Raises:** HTTPException: 404 - Setting not found by key.

    **Returns:** Setting.
    """

    # Check if the setting exists (by key)
    db_setting = db.query(Settings).filter(Settings.key == key).first()

    # If the setting doesn't exist, raise an exception
    if db_setting is None:
        raise HTTPException(
            status_code=404, detail=f"Setting with key: {key} not found"
        )

    # Return the setting by key
    return db_setting


# Update a setting by key
@settings.put(
    "/settings/{key}",
    response_model=Setting,
    summary="Update a setting by key",
    status_code=status.HTTP_200_OK,
)
def update_setting(key: str, setting: Setting, db: Session = Depends(get_db)):

    """
    Update a setting of the system by key from the database.

    **Raises:** HTTPException: 404 - Setting not found by key.

    **Returns:** Setting updated.
    """

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
@settings.delete(
    "/settings/{key}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a setting by key",
)
def delete_setting(key: str, db: Session = Depends(get_db)):

    """
    Delete a setting of the system by key from the database.

    **Raises:** HTTPException: 404 - Setting not found by key.

    **Returns:** Status code: 204 - No Content
    """

    db_setting = db.query(Settings).filter(Settings.key == key).first()

    if db_setting is None:
        raise HTTPException(
            status_code=404, detail=f"Setting with key: {key} not found"
        )

    db.delete(db_setting)
    db.commit()

    return status.HTTP_204_NO_CONTENT
