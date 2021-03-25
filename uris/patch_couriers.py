from typing import List, Optional
from fastapi import APIRouter
from pydantic.main import BaseModel
from fastapi.responses import JSONResponse

from models.courier import Courier


class CourierPatchSchemaRequest(BaseModel):
    courier_type: Optional[str]
    regions: Optional[List[int]]
    working_hours: Optional[List[str]]

    class Config:
        schema_extra = {
            'example':
                {
                    'courier_type': 'car',
                    'regions': [11, 33, 2],
                    'working_hours': ['14:14-19:19']
                }
        }


class CourierPatchSchemaResponse(BaseModel):
    courier_id: int
    courier_type: str
    regions: List[int]
    working_hours: List[str]

    class Config:
        schema_extra = {
            'example':
                {
                    'courier_id': 2,
                    'courier_type': 'foot',
                    'regions': [11, 33, 2],
                    'working_hours': ["09:00-18:00"]
                }
        }


patch_couriers_route = APIRouter()


@patch_couriers_route.patch('/couriers/{id}', responses={200: {'model': CourierPatchSchemaResponse}, 400: {}, 404: {}})
async def update_courier(id: int, request: CourierPatchSchemaRequest):
    try:
        # Если в поступившем реквесте нет данных, которые требуется обновить, то возвращаем 400 response
        if not request.dict(exclude_none=True):
            return JSONResponse(status_code=400)
        courier = await Courier.get(id=id)
        if 'courier_type' in request.dict(exclude_none=True):
            courier.type = request.dict()['courier_type']
        if 'regions' in request.dict(exclude_none=True):
            courier.regions = request.dict()['regions']
        if 'working_hours' in request.dict(exclude_none=True):
            courier.working_hours = request.dict()['working_hours']
        await courier.check()
        await courier.save()
        return CourierPatchSchemaResponse(**courier.dict())

    except ValueError as e:
        if str(e) == 'Courier with this id does not exist':
            return JSONResponse(status_code=404)
        else:
            print(str(e))
            return JSONResponse(status_code=400)
