from typing import List, Dict, Optional
from fastapi import APIRouter
from fastapi.responses import JSONResponse
from pydantic import BaseModel

from models.courier import Courier


class OrdersAssignSchemaRequest(BaseModel):
    courier_id: int

    class Config:
        schema_extra = {
            'example':
                {
                    'courier_id': 2
                }
        }


class OrdersAssignSchemaResponse(BaseModel):
    orders: List
    assign_time: Optional[str]

    class Config:
        schema_extra = {
            'example':
                {
                    'orders': [{'id': 1}, {'id': 2}],
                    'assign_time': '2021-01-10T09:32:14.422'
                }
        }


post_orders_assign_route = APIRouter()


@post_orders_assign_route.post('/orders/assign',
                               responses={400: {}, 200: {'model': OrdersAssignSchemaResponse}})
async def orders_assign(request: OrdersAssignSchemaRequest):
    #try:
        courier = await Courier.get(id=request.courier_id)
        await courier.find_and_assign_orders()
        if not courier.assigns:
            return OrdersAssignSchemaResponse(orders=[])
        return OrdersAssignSchemaResponse(orders=[{'id': i} for i in courier.assigns],
                                          assign_time=courier.assign_time.isoformat())
    #except ValueError as e:
    #    print(str(e))
    #    return JSONResponse(status_code=400)

