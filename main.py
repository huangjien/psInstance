from fastapi.testclient import TestClient

from apis.base import api_router
import motor.motor_asyncio
import uvicorn as uvicorn
from decouple import config
from fastapi import FastAPI

# settings section
from db.model import DBConnection

PORT = config('PORT', default=8080, cast=int)
HOST = config('HOST', default="0.0.0.0")

app = FastAPI(name="Deployment", docs_url="/docs", redoc_url="/redoc",
              version='0.1.1', openapi_url="/openapi.json",
              title="Deployment", description="Deployment")
app.include_router(api_router, prefix="/api/v1")


async def open_db() -> motor.motor_asyncio.AsyncIOMotorClient:
    DBConnection.instance().client


async def close_db():
    DBConnection.instance().client.close()


app.add_event_handler('startup', open_db)
app.add_event_handler('shutdown', close_db)


@app.get("/")
async def root():
    return {"status": "SUCCESS"}


client = TestClient(app)


def test_root():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"status": "SUCCESS"}


if __name__ == "__main__":
    uvicorn.run(app, host=HOST, port=PORT)
