import os
from fastapi import FastAPI, Body, HTTPException, status
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder
from pydantic import BaseModel, Field, EmailStr
from bson import ObjectId
from typing import Optional, List
import motor.motor_asyncio

MONGO_DETAILS = "mongodb://localhost:27017"

app = FastAPI()
client = motor.motor_asyncio.AsyncIOMotorClient(MONGO_DETAILS)
db = client.test


class PyObjectId(ObjectId):
    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, v):
        if not ObjectId.is_valid(v):
            raise ValueError("Invalid objectid")
        return ObjectId(v)

    @classmethod
    def __modify_schema__(cls, field_schema):
        field_schema.update(type="string")


class SettingModel(BaseModel):
    name: str = Field(..., index=True)
    value: str = Field(...)
    category: str = Field(..., index=True)
    description: str = Field(...)

    class Config:
        allow_population_by_field_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}


@app.post("/setting/", response_model=SettingModel)
async def create_setting(setting: SettingModel = Body(..., embed=True)):
    setting = jsonable_encoder(setting)
    new_setting = await db.settings.insert_one(setting)
    created_setting = await db.settings.find_one({"name": new_setting.inserted_id})
    return JSONResponse(status_code=status.HTTP_201_CREATED, content=created_setting)


@app.get("/setting/", response_model=List[SettingModel])
async def get_settings():
    settings = await db.settings.find().to_list(None)
    return settings


@app.get("/setting/{setting_id}", response_model=SettingModel)
async def get_setting(setting_id: str):
    if (setting := await db.settings.find_one({"name": setting_id})) is not None:
        return setting
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Setting {setting_id} not found")


@app.get("/")
async def root():
    return {"status": "SUCCESS"}
