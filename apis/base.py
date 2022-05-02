from fastapi import APIRouter

from apis import route_setting, route_deployment

api_router = APIRouter()
api_router.include_router(route_setting.router, prefix="/setting", tags=["setting"])
api_router.include_router(route_deployment.router, prefix="/deployment", tags=["deployment"])
