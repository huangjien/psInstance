from urllib.request import Request

import uvicorn as uvicorn
from cachetools.func import ttl_cache
from fastapi import FastAPI, Body, HTTPException, status
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder
from typing import List
from decouple import config
import motor.motor_asyncio

from model import SettingModel

# settings section
PORT = config('PORT', default=8000, cast=int)
HOST = config('HOST', default="0.0.0.0")
DB_NAME = config('DB_NAME', default='test')
MONGO_URL = config("MONGO_URL", default="mongodb://localhost:27017")

app = FastAPI()


async def open_db() -> motor.motor_asyncio.AsyncIOMotorClient:
    app.state.mongodb = motor.motor_asyncio.AsyncIOMotorClient(MONGO_URL)[DB_NAME]


async def close_db():
    app.state.mongodb.close()


app.add_event_handler('startup', open_db)
app.add_event_handler('shutdown', close_db)


@app.post("/setting/", response_model=SettingModel)
async def create_setting(setting: SettingModel = Body(..., embed=True)):
    setting = jsonable_encoder(setting)
    new_setting = await app.state.mongodb.settings.insert_one(setting)
    created_setting = await app.state.mongodb.settings.find_one({"name": new_setting.inserted_id})
    return JSONResponse(status_code=status.HTTP_201_CREATED, content=created_setting)


@ttl_cache(maxsize=64, ttl=600)
@app.get("/setting/", response_model=List[SettingModel])
async def get_settings():
    settings = await app.state.mongodb.settings.find().to_list(None)
    return settings


@ttl_cache(maxsize=64, ttl=600)
@app.get("/setting/{setting_id}", response_model=SettingModel)
async def get_setting(setting_id: str):
    if (setting := await app.state.mongodb.settings.find_one({"name": setting_id})) is not None:
        return setting
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Setting {setting_id} not found")


@app.get("/")
async def root():
    return {"status": "SUCCESS"}


if __name__ == "__main__":
    uvicorn.run(app, host=HOST, port=PORT)
