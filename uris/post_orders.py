from typing import List, Dict
from fastapi import APIRouter
from pydantic import BaseModel

from models.order import Order

post_orders_route = APIRouter()


class OrdersSchemaRequest(BaseModel):
    data: List['Order']

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
                    'validation_error': [{'id': 1}, {'id': 2}, {'id': 3}]
                }
        }


@post_orders_route.post('/orders', responses={400: {'model': OrdersSchemaResponse400},
                                              201: {'model': OrdersSchemaResponse201}})
async def list_of_orders(request: OrdersSchemaRequest):
    errors = []
    succeeded: List['Order'] = []
    for order in request.data:
        try:
            succeeded.append(Order(**order.dict()))
        except ValueError:
            errors.append(order.order_id)
    if not errors:
        for order in succeeded:
            await order.create()
        return OrdersSchemaResponse201(orders=[{'id': order.order_id} for order in succeeded])
    else:
        return OrdersSchemaResponse400(validation_error=[{'id': order} for order in errors])
