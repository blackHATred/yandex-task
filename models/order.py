from pydantic import BaseModel, validator
import re
from typing import List, Optional
from tortoise.models import Model
from tortoise import fields


class Order(BaseModel):
    order_id: int                 # айди заказа - 1
    weight: float                 # вес заказа - 2.42
    region: int                   # район, в который нужно доставить - 1
    delivery_hours: List[str]     # время доставки - ["12:00-14:00", "15:30-17:30"]
    courier_id: Optional[int]     # айди назначенного курьера - 1
    completed: Optional[bool]     # заказ доставлен - True/False
    complete_time: Optional[int]  # за какое время доставлен (в секундах) - 300

    @validator('delivery_hours')
    def delivery_hours_validator(cls, v: list):
        if len(v) == 0:
            raise ValueError('List of delivery hours cannot be empty')
        for i in v:
            if not isinstance(i, str):
                raise ValueError('delivery hours must be list of strings')
            elif not re.fullmatch('[0-2][0-9]:[0-5][0-9]-[0-2][0-9]:[0-5][0-9]', i) or \
                    24 <= int(i[0:2]) or 24 <= int(i[6:8]):
                raise ValueError('Incorrect format of delivery hours')
        return v

    @validator('weight')
    def type_validator(cls, v: float):
        if v > 50 or v < 0.01:
            raise ValueError('Weight must be bigger than 0.01 and less than 50 kilograms')
        return v

    async def create(self):
        if await OrderDB.exists(order_id=self.order_id):
            raise ValueError('Order with this id already exists')
        else:
            await OrderDB.create(
                id=self.order_id,
                weight=self.weight,
                region=self.region,
                delivery_hours=','.join(self.delivery_hours)
            )

    @staticmethod
    async def get(id: int) -> 'Order':
        """
        Получает модель из БД и возвращает её репрезентацию
        :param id: id заказа
        :return: репрезентация типа Order
        """
        if await OrderDB.exists(order_id=id):
            order = await OrderDB.get(order_id=id)
            return Order(**order.dump())
        else:
            raise ValueError('Order with this id does not exist')

    async def save(self):
        """
        Сохраняет изменённую модель в БД.
        :return: ValueError при неудачной валидации
        """
        order_db = await OrderDB.get(order_id=self.order_id)
        updated_order = Order(**self.dict())
        await order_db.update(data=updated_order.dict())


class OrderDB(Model):
    order_id = fields.IntField(pk=True)
    weight = fields.FloatField()
    region = fields.IntField()
    delivery_hours = fields.TextField()
    courier_id = fields.IntField(null=True, default=None)
    completed = fields.BooleanField(default=False)
    complete_time = fields.IntField(null=True, default=None)

    def dump(self):
        """
        Возращает свою репрезентацию в виде словаря
        :return: dict
        """
        return {
            'order_id': self.order_id,
            'weight': self.weight,
            'region': self.region,
            'delivery_hours': [*self.delivery_hours.split(',')],
            'courier_id': self.courier_id,
            'completed': self.completed,
            'complete_time': self.complete_time
        }

    async def update(self, data: dict):
        """
        Обновляет данные в БД
        :param data: данные для обновления
        :return: None
        """
        if 'delivery_hours' in data.keys():
            data['delivery_hours'] = ','.join(data['delivery_hours'])
        await self.update_from_dict(data=data)
        await self.save()

