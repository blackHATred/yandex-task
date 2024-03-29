from typing import List, Dict
from fastapi import APIRouter
from pydantic.main import BaseModel
from fastapi.responses import JSONResponse

from models.courier import Courier


class CouriersSchemaRequest(BaseModel):
    data: List

    class Config:
        schema_extra = {
            'example':
                {
                    'data': [
                        Courier(courier_id=1,
                                courier_type='foot',
                                regions=[1, 12, 22],
                                working_hours=['11:35-14:05', '09:00-11:00']),
                        Courier(courier_id=2,
                                courier_type='bike',
                                regions=[22],
                                working_hours=['09:00-18:00']),
                        Courier(courier_id=3,
                                courier_type='car',
                                regions=[12, 22, 23, 33],
                                working_hours=['09:00-11:00'])
                    ]
                }
        }


class CouriersSchemaResponse201(BaseModel):
    couriers: List[Dict]

    class Config:
        schema_extra = {
            'example':
                {
                    'couriers': [{'id': 1}, {'id': 2}, {'id': 3}]
                }
        }


class CouriersSchemaResponse400(BaseModel):
    validation_error: Dict

    class Config:
        schema_extra = {
            'example':
                {
                    'validation_error': {'couriers': [{'id': 1}, {'id': 2}, {'id': 3}]}
                }
        }


post_couriers_route = APIRouter()


@post_couriers_route.post('/couriers', responses={400: {'model': CouriersSchemaResponse400},
                                                  201: {'model': CouriersSchemaResponse201}})
async def list_of_couriers(request: CouriersSchemaRequest):
    errors = []
    succeeded = []
    ids = [courier['courier_id'] for courier in request.data]

    for courier in request.data:
        try:
            valid_courier = Courier(**courier)
            if await Courier.exists(valid_courier.courier_id) or ids.count(valid_courier.courier_id) != 1:
                raise ValueError
            else:
                succeeded.append(valid_courier)
        except ValueError:
            errors.append(courier['courier_id'])

    if not errors:
        for courier in succeeded:
            await courier.create()
        return JSONResponse(status_code=201, content={
            'couriers': [{'id': courier.courier_id} for courier in succeeded]
        })
    else:
        return JSONResponse(status_code=400, content={
            'validation_error': {'couriers': [{'id': i} for i in errors]}
        })
