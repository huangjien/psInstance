from typing import Optional

import motor
from bson import ObjectId
from decouple import config
from pydantic import BaseModel, Field
from bson.objectid import ObjectId as BSONObjectId

DB_NAME = config('DB_NAME', default='test')
MONGO_URL = config("MONGO_URL", default="mongodb://localhost:27017")


class Singleton:
    def __init__(self, cls):
        self._cls = cls

    def instance(self):
        try:
            return self._instance
        except AttributeError:
            self._instance = self._cls()
            return self._instance

    def __call__(self):
        raise TypeError('Singletons must be accessed through `Instance()`.')

    def __instancecheck__(self, inst):
        return isinstance(inst, self._cls)


@Singleton
class DBConnection(object):
    def __init__(self):
        self.client = motor.motor_asyncio.AsyncIOMotorClient(MONGO_URL, maxPoolSize=50)
        self.db = self.client[DB_NAME]
        pass

    def __str__(self):
        return '<DBConnection> {}'.format(self.client)

    def close(self):
        self.client.close()


class PyObjectId(ObjectId):
    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, v):
        if not isinstance(v, BSONObjectId):
            raise TypeError('ObjectId required')
        return str(v)

    @classmethod
    def __modify_schema__(cls, field_schema):
        field_schema.update(type="string")


# Setting of the system
class SettingModel(BaseModel):
    name: str = Field(..., index=True)
    value: str = Field(...)
    category: str = Field(..., index=True)
    description: str = Field(...)

    class Config:
        allow_population_by_field_name = True
        arbitrary_types_allowed = True


# Deployment data model
class DeploymentModel(BaseModel):
    name: str = Field(..., index=True)
    description: str = Field(...)
    owners: list = Field(...)
    softwares: list = Field(...)
    environments: Optional[dict] = Field(None)
    status: dict = Field(...)
