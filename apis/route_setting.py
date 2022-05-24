from typing import List
from fastapi import APIRouter, Body, HTTPException
from fastapi.encoders import jsonable_encoder
from starlette import status
from db.model import SettingModel, DBConnection, timed_lru_cache, cacheable

router = APIRouter()


@router.post("/create/", response_model=SettingModel)
async def create_setting(setting: SettingModel = Body(..., embed=True)):
    setting = jsonable_encoder(setting)
    await DBConnection.instance().db.settings.insert_one(setting)
    created_setting = await DBConnection.instance().db.settings.find_one({"name": setting.get("name")})
    return created_setting


@router.put("/update/{name}", response_model=SettingModel)
async def update_setting(name: str, setting: SettingModel = Body(..., embed=True)):
    setting = jsonable_encoder(setting)
    await DBConnection.instance().db.settings.update_one({"name": name}, {"$set": setting})
    updated_setting = await DBConnection.instance().db.settings.find_one({"_id": name})
    return updated_setting


@router.delete("/delete/{name}", response_model=SettingModel)
async def delete_setting(name: str):
    await DBConnection.instance().db.settings.delete_one({"name": name})
    return {"name": name, "deleted": True}


@timed_lru_cache
@cacheable
@router.get("/list/", response_model=List[SettingModel])
async def get_settings():
    settings = await DBConnection.instance().db.settings.find().to_list(None)
    return settings


@timed_lru_cache
@cacheable
@router.get("/name/{setting_id}", response_model=SettingModel)
async def get_setting_by_name(name: str):
    if (setting := await DBConnection.instance().db.settings.find_one({"name": name})) is not None:
        return setting
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Setting by name {name} not found")


@timed_lru_cache
@cacheable
@router.get("/category/{category}", response_model=SettingModel)
async def get_setting_by_category(category: str):
    if (setting := await DBConnection.instance().db.settings.find_one({"category": category})) is not None:
        return setting
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Setting by category {category} not found")