import asyncio
from datetime import datetime
from functools import lru_cache, wraps
from typing import Optional
import motor
from bson import ObjectId
from decouple import config
from pydantic import BaseModel, Field, EmailStr
from bson.objectid import ObjectId as BSONObjectId

DB_NAME = config('DB_NAME', default='test')
MONGO_URL = config("MONGO_URL", default="mongodb://localhost:27017")

class Cacheable:
    def __init__(self, co):
        self.co = co
        self.done = False
        self.result = None
        self.lock = asyncio.Lock()

    def __await__(self):
        while (yield from self.lock):
            if self.done:
                return self.result
            self.result = yield from self.co.__await__()
            self.done = True
            return self.result

def cacheable(f):
    def wrapper(*args, **kwargs):
        return Cacheable(f(*args, **kwargs))
    return wrapper


def timed_lru_cache(seconds: int = 300, maxsize: int = 128):
    def wrapper_cache(f):
        f = lru_cache(maxsize = maxsize)(f)
        f.life_time = datetime.timedelta(seconds = seconds)
        f.expiration = datetime.utcnow() + f.life_time

        @wraps(f)
        def wrapper(*args, **kwargs):
            if datetime.utcnow() > f.expiration:
                f.cache_clear()
                f.expiration = datetime.utcnow() + f.life_time
            return f(*args, **kwargs)
        return wrapper
    return wrapper_cache


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
        raise TypeError('Singletons must be accessed through `instance()`.')

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
    name: str = Field(..., index=True)  # name of the deployment, usually the name of the machine
    url: str = Field(..., index=True)  # url of the deployment
    osinfo: list[dict] = Field(...)  # os info of the deployment
    description: str = Field(...)
    owners: list[EmailStr] = Field(...)
    softwares: list[dict] = Field(...)
    environments: Optional[list[dict]] = Field(None)
    status: list[dict] = Field(...)
