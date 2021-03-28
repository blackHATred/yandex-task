from typing import List, Dict
from fastapi import APIRouter
from pydantic import BaseModel
from fastapi.responses import JSONResponse

from models.order import Order

post_orders_route = APIRouter()


class OrdersSchemaRequest(BaseModel):
    data: List

    class Config:
        schema_extra = {
            'example':
                {
                    'data': [
                        Order(order_id=1,
                              weight=0.23,
                              region=12,
                              delivery_hours=["09:00-18:00"]),
                        Order(order_id=2,
                              weight=15,
                              region=1,
                              delivery_hours=["09:00-18:00"]),
                        Order(order_id=3,
                              weight=0.01,
                              region=22,
                              delivery_hours=["09:00-12:00", "16:00-21:30"])
                    ]
                }
        }


class OrdersSchemaResponse201(BaseModel):
    orders: List[Dict]

    class Config:
        schema_extra = {
            'example':
                {
                    'orders': [{'id': 1}, {'id': 2}, {'id': 3}]
                }
        }


class OrdersSchemaResponse400(BaseModel):
    validation_error: List[Dict]

    class Config:
        schema_extra = {
            'example':
                {
                    'validation_error': {'orders': [{'id': 1}, {'id': 2}, {'id': 3}]}
                }
        }


@post_orders_route.post('/orders', responses={400: {'model': OrdersSchemaResponse400},
                                              201: {'model': OrdersSchemaResponse201}})
async def list_of_orders(request: OrdersSchemaRequest):
    errors = []
    succeeded = []
    ids = [order['order_id'] for order in request.data]

    for order in request.data:
        try:
            valid_order = Order(**order)
            if await Order.exists(valid_order.order_id) or ids.count(valid_order.order_id) != 1:
                raise ValueError
            else:
                succeeded.append(valid_order)
        except ValueError:
            errors.append(order['order_id'])
    if not errors:
        for order in succeeded:
            await order.create()
        return JSONResponse(status_code=201, content={
            'orders': [{'id': order.order_id} for order in succeeded]
        })
    else:
        return JSONResponse(status_code=400, content={
            'validation_error': {'orders': [{'id': order} for order in errors]}
        })
