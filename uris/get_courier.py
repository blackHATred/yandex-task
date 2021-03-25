from typing import List
from fastapi import APIRouter
from fastapi.responses import JSONResponse
from pydantic.main import BaseModel

from models.courier import Courier


class GetCourierSchemaResponse(BaseModel):
    courier_id: int = 2
    courier_type: str = 'foot'
    regions: List[int] = [11, 33, 2]
    working_hours: List[str] = ['09:00-18:00']
    rating: float = 4.93
    earnings: int = 10000


get_couriers_route = APIRouter()


@get_couriers_route.get('/couriers/{id}', responses={404: {}, 200: {'model': GetCourierSchemaResponse}})
async def get_courier(id: int):
    # В задании нет некоторых уточнений, поэтому при рассчёте рейтинга учитываются даже те районы,
    # в которых курьер уже не работает (К примеру курьер развозил посылки по району 1, но через
    # PATCH ему заменили район 1 на район 2. Рейтинг будет рассчитываться с учётом работы по 1 району в прошлом)
    try:
        courier = await Courier.get(id=id)
        return GetCourierSchemaResponse(
            courier_id=courier.courier_id,
            courier_type=courier.courier_type,
            regions=courier.regions,
            working_hours=courier.working_hours,
            rating=(await courier.get_rating()),
            earnings=courier.earnings
        )
    except ValueError:
        return JSONResponse(status_code=404)
