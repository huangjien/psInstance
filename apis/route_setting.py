from typing import List

from cachetools.func import ttl_cache
from fastapi import APIRouter, Body, HTTPException
from fastapi.encoders import jsonable_encoder
from starlette import status

from db.model import SettingModel, DBConnection

# from main import app

router = APIRouter()


@router.post("/setting/", response_model=SettingModel)
async def create_setting(setting: SettingModel = Body(..., embed=True)):
    setting = jsonable_encoder(setting)
    await DBConnection.instance().db.settings.insert_one(setting)
    created_setting = await DBConnection.instance().db.settings.find_one({"name": setting.get("name")})
    return created_setting


@ttl_cache(maxsize=64, ttl=600)
@router.get("/settings/", response_model=List[SettingModel])
async def get_settings():
    settings = await DBConnection.instance().db.settings.find().to_list(None)
    return settings


@ttl_cache(maxsize=64, ttl=600)
@router.get("/setting/{setting_id}", response_model=SettingModel)
async def get_setting(setting_id: str):
    if (setting := await DBConnection.instance().db.settings.find_one({"name": setting_id})) is not None:
        return setting
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Setting {setting_id} not found")
