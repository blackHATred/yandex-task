from fastapi import APIRouter
from fastapi.responses import JSONResponse
from pydantic import validator
from pydantic.main import BaseModel
from datetime import datetime

from models.courier import Courier
from models.order import Order


class OrderCompleteSchemaRequest(BaseModel):
    courier_id: int
    order_id: int
    complete_time: str

    @validator('complete_time')
    def time_validator(cls, v: str):
        # превращаем строку в datetime и затем обратно в строку с целью валидации на соответствие iso формату
        return datetime.fromisoformat(v).isoformat()

    class Config:
        schema_extra = {
            'example':
                {
                    'courier_id': 2,
                    'order_id': 33,
                    'complete_time': '2021-01-10T10:33:01.422'
                }
        }


class OrderCompleteSchemaResponse(BaseModel):
    order_id: int

    class Config:
        schema_extra = {
            'example':
                {
                    'order_id': 2,
                }
        }


post_orders_complete_route = APIRouter()


@post_orders_complete_route.post('/orders/complete', responses={400: {}, 200: {'model': OrderCompleteSchemaResponse}})
async def order_complete(request: OrderCompleteSchemaRequest):
    try:
        order = await Order.get(request.order_id)
        if order.courier_id != request.courier_id:
            raise ValueError
        if order.completed:
            return OrderCompleteSchemaResponse(order_id=order.order_id)
        courier = await Courier.get(id=order.courier_id)

        courier.earnings += {'car': 9, 'bike': 5, 'foot': 2}[courier.courier_type] * 500
        courier.assigns.remove(order.order_id)
        courier.completed.append(order.order_id)
        order.completed = True
        if courier.last_completed is None or courier.assign_time > courier.last_completed:
            order.complete_time = (
                    datetime.fromisoformat(request.complete_time) - courier.assign_time.replace(tzinfo=None)
            ).total_seconds()
        else:
            order.complete_time = (
                    datetime.fromisoformat(request.complete_time) - courier.last_completed.replace(tzinfo=None)
            ).total_seconds()
        courier.last_completed = datetime.fromisoformat(request.complete_time)

        await courier.save()
        await order.save()
        return OrderCompleteSchemaResponse(order_id=order.order_id)

    except ValueError:
        return JSONResponse(status_code=400)
