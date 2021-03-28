from pydantic import BaseModel, validator
import re
from typing import List, Optional, Union
from tortoise.models import Model
from tortoise import fields
from tortoise.query_utils import Q
from datetime import datetime


from models.order import Order, OrderDB
from helpers.time_translate import time_to_int_intervals


class Courier(BaseModel):
    courier_id: int                                   # айди курьера - 1
    courier_type: str                                 # тип курьера - 'foot', 'bike' или 'car'
    regions: List[int]                                # районы - [1, 2, 3]
    working_hours: List[str]                          # время работы - ["12:00-14:00", "15:30-17:30"]
    assign_time: Optional[Union[datetime, None]]      # время назначения заказов - datetime
    assigns: Optional[Union[List[int], None]]         # id назначенных заказов - [1, 2, 3]
    completed: Optional[Union[List[int], None]]       # id выполненных заказов - [1, 2, 3]
    last_completed: Optional[Union[datetime, None]]   # время выполнения последнего заказа - datetime
    earnings: Optional[int]                           # заработок - 10000

    @validator('working_hours')
    def working_hours_validator(cls, v: list):
        if len(v) == 0:
            raise ValueError('List of working hours cannot be empty')
        for i in v:
            if not isinstance(i, str):
                raise ValueError('Working hours must be list of strings')
            elif not re.fullmatch('[0-2][0-9]:[0-5][0-9]-[0-2][0-9]:[0-5][0-9]', i) or \
                    24 <= int(i[0:2]) or 24 <= int(i[6:8]):
                raise ValueError('Incorrect format of working hours')
        return v

    @validator('courier_type')
    def type_validator(cls, v: str):
        if v not in ('foot', 'bike', 'car'):
            raise ValueError('Courier type must be "foot", "bike" or "car"')
        return v

    @validator('regions')
    def regions_validator(cls, v: list):
        if len(v) == 0:
            raise ValueError('List of regions cannot be empty')
        return v

    async def can_deliver(self, order_interval: List[int], weight: float) -> bool:
        """
        Проверяет, может ли курьер доставить заказ (проверка по весу и диапазону времени)
        :param weight: Вес посылки
        :param order_interval: Диапазон времени для доставки в формате [с (int), до (int)], int - минуты
        :return: bool
        """
        orders_weight = 0
        for assign in self.assigns:
            order = await Order.get(assign)
            orders_weight += order.weight
        max_weight = {'car': 50, 'bike': 12, 'foot': 10}[self.courier_type]
        if orders_weight + weight <= max_weight:
            # если подходит по весу, то проверяем наличие пересечения временных интервалов доставки и работы
            for interval in time_to_int_intervals(self.working_hours):
                if (interval[0] <= order_interval[0] <= interval[1]
                        or interval[0] <= order_interval[1] <= interval[1]
                        or order_interval[0] <= interval[0] <= order_interval[1]
                        or order_interval[0] <= interval[1] <= order_interval[1]):
                    return True
        return False

    async def create(self):
        """
        Сохраняет созданную модель в БД
        :return: None
        """
        if await CourierDB.exists(courier_id=self.courier_id):
            raise ValueError('Courier with this id already exists')
        else:
            await CourierDB.create(
                courier_id=self.courier_id,
                courier_type=self.courier_type,
                regions=','.join(map(str, self.regions)),
                working_hours=','.join(self.working_hours)
            )

    async def save(self):
        """
        Обновляет изменённую модель в БД.
        :return: ValueError при неудачной валидации
        """
        courier_db = await CourierDB.get(courier_id=self.courier_id)
        updated_courier = Courier(**self.dict())
        await courier_db.update(data=updated_courier.dict())

    @staticmethod
    async def get(id: int) -> 'Courier':
        """
        Получает модель из БД и возвращает её репрезентацию
        :param id: id курьера
        :return: репрезентация типа Courier
        """
        if await CourierDB.exists(courier_id=id):
            courier = await CourierDB.get(courier_id=id)
            return Courier(**courier.dump())
        else:
            raise ValueError('Courier with this id does not exist')

    @staticmethod
    async def exists(id: int) -> bool:
        """
        Проверяет сущестовавние заказа с указанным id
        :return: True/False
        """
        return await CourierDB.exists(courier_id=id)

    async def find_and_assign_orders(self):
        """
        Находит и назначает подходящие по времени и весу заказы курьеру
        :return: None
        """
        max_weight = {'car': 50, 'bike': 12, 'foot': 10}[self.courier_type]
        # Сортировка подходящих заказов по
        # 1) регионам, совпадающими с теми, в которых работает курьер
        # 2) весу, который должен быть меньше максимально допустимого для типа определённого курьера
        # 3) айди курьера, который должен отсутствовать
        # 4) статусу. Заказ не должен быть выполнен
        orders = await OrderDB.filter(
            Q(region__in=self.regions) &
            Q(weight__lte=max_weight) &
            Q(courier_id__isnull=True) &
            Q(completed=False)
        )
        # Подбираем заказы, у которых время доставки пересекается с временем работы курьера
        # и которые подойдут по весу с учётом уже присвоенных заказов
        for order in orders:
            for interval in time_to_int_intervals(order.delivery_hours):
                if await self.can_deliver(order_interval=interval, weight=order.weight):
                    if not self.assigns:
                        self.assign_time = datetime.utcnow()
                    self.assigns.append(order.order_id)
                    order.courier_id = self.courier_id
                    await order.save()
                    # не имеет смысла проверять последующие интервалы доставки, поэтому выходим из цикла для проверки
                    # следующего заказа
                    break
        await self.save()

    async def get_rating(self) -> float:
        """
        Высчитывает и возвращает рейтинг курьера
        :return: рейтинг float (:.2f)
        """
        # создаём словарь, где каждому району соответствует массив с временем выполнения каждого заказа
        # в этом районе
        regions_and_time = dict()
        for order in self.completed:
            o = await Order.get(order)
            if o.region not in regions_and_time.keys():
                regions_and_time.update({o.region: [o.complete_time]})
            else:
                regions_and_time[o.region].append(o.complete_time)
        # высчитываем среднее время доставки заказа в каждом районе
        for time in regions_and_time.keys():
            regions_and_time[time] = sum(regions_and_time[time])/len(regions_and_time[time])
        # высчитываем и возвращаем рейтинг с округлением до двух знаков после запятой
        return round((3600 - min(min(regions_and_time.values()), 3600))/3600 * 5, 2)

    async def check(self):
        """
        Проверяет уже назначенные заказы на возможность доставки (используется при обновлении типа/регионов/времени)
        :return: None
        """
        assigns = list()
        for order in self.assigns:
            o = await Order.get(id=order)
            o.courier_id = None
            await o.save()
            assigns.append(o)
        self.assigns = []
        for assign in assigns:
            for interval in time_to_int_intervals(assign.delivery_hours):
                if await self.can_deliver(interval, assign.weight):
                    self.assigns.append(assign.order_id)
                    assign.courier_id = self.courier_id
                    await assign.save()
                    break
        await self.save()


class CourierDB(Model):
    courier_id = fields.IntField(pk=True)
    courier_type = fields.CharField(max_length=4)
    regions = fields.TextField()
    working_hours = fields.TextField()
    assign_time = fields.DatetimeField(default=None, null=True)
    assigns = fields.TextField(default='', null=True)
    completed = fields.TextField(default='', null=True)
    last_completed = fields.DatetimeField(default=None, null=True)
    earnings = fields.IntField(default=0)

    def dump(self) -> dict:
        """
        Возращает свою репрезентацию в виде словаря
        :return: dict
        """
        return {
            'courier_id': self.courier_id,
            'courier_type': self.courier_type,
            'regions': [*map(int, self.regions.split(','))] if self.regions != '' else [],
            'working_hours': [*self.working_hours.split(',')] if self.working_hours != '' else [],
            'assign_time': self.assign_time,
            'assigns': [*map(int, self.assigns.split(','))] if self.assigns != '' else [],
            'completed': [*map(int, self.completed.split(','))] if self.completed != '' else [],
            'last_completed': self.last_completed,
            'earnings': self.earnings
        }

    async def update(self, data: dict):
        """
        Обновляет данные в БД
        :param data: данные для обновления
        :return: None
        """
        if 'regions' in data.keys():
            data['regions'] = ','.join(map(str, data['regions']))
        if 'working_hours' in data.keys():
            data['working_hours'] = ','.join(data['working_hours'])
        if 'assigns' in data.keys():
            data['assigns'] = ','.join(map(str, data['assigns']))
        if 'completed' in data.keys():
            data['completed'] = ','.join(map(str, data['completed']))
        await self.update_from_dict(data=data)
        await self.save()
