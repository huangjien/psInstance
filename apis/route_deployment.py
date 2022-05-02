from typing import List

from cachetools.func import ttl_cache
from fastapi import APIRouter, HTTPException
from starlette import status
from db.model import DeploymentModel, DBConnection


router = APIRouter()


@ttl_cache(maxsize=64, ttl=600)
@router.get("/deployments/", response_model=List[DeploymentModel])
async def get_deployments():
    settings = await DBConnection.instance().db.deployments.find().to_list(None)
    return settings


@ttl_cache(maxsize=64, ttl=600)
@router.get("/deployment/{name}", response_model=DeploymentModel)
async def get_deployment(name: str):
    if (setting := await DBConnection().instance().db.deployments.find_one({"name": name})) is not None:
        return setting
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Deployment {name} not found")


@router.post("/deployment/", response_model=DeploymentModel)
async def create_deployment(deployment: DeploymentModel):
    if (setting := await DBConnection().instance().db.deployments.find_one({"name": deployment.name})) is not None:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=f"Deployment {deployment.name} already exists")
    await DBConnection().instance().db.deployments.insert_one(deployment)
    return deployment


@router.put("/deployment/{name}", response_model=DeploymentModel)
async def update_deployment(name: str, deployment: DeploymentModel):
    if (setting := await DBConnection().instance().db.deployments.find_one({"name": name})) is not None:
        await DBConnection().instance().db.deployments.update_one({"name": name}, {"$set": deployment})
        return deployment
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Deployment {name} not found")


@router.delete("/deployment/{name}")
async def delete_deployment(name: str):
    if (setting := await DBConnection().instance().db.deployments.find_one({"name": name})) is not None:
        await DBConnection().instance().db.deployments.delete_one({"name": name})
        return {"deleted": True, "deployment": setting}
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Deployment {name} not found")
