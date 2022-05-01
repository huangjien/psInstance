from db.model import DeploymentModel, DBConnection
from typing import List

from cachetools.func import ttl_cache
from fastapi import APIRouter, Body, HTTPException
from fastapi.encoders import jsonable_encoder
from starlette import status
from starlette.responses import JSONResponse
# from main import app

router = APIRouter()


@ttl_cache(maxsize=64, ttl=600)
@router.get("/deployments/", response_model=List[DeploymentModel])
async def get_deployments():
    settings = await DBConnection.instance().db.deployments.find().to_list(None)
    return settings


@ttl_cache(maxsize=64, ttl=600)
@router.get("/deployment/{deployment_id}", response_model=DeploymentModel)
async def get_deployment(deployment_id: str):
    if (setting := await DBConnection().instance().db.deployments.find_one({"name": deployment_id})) is not None:
        return setting
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Deployment {deployment_id} not found")
