from typing import Generator
import asyncio
from fastapi.testclient import TestClient
import pytest
from tortoise.contrib.test import finalizer, initializer
import datetime as dt

from main import app

client = TestClient(app)


@pytest.fixture(scope="module")
def client() -> Generator:
    initializer(["models"])
    with TestClient(app) as c:
        yield c
    finalizer()


@pytest.fixture(scope="module")
def event_loop(client: TestClient) -> Generator:
    yield client.task.get_loop()


def test_post_couriers(client: TestClient, event_loop: asyncio.AbstractEventLoop):
    # проверяем, как сервер отреагирует на валидные данные
    response = client.post('/couriers', json={
        'data': [
            {
                'courier_id': 1,
                'courier_type': 'foot',
                'regions': [1, 2, 3],
                'working_hours': ['11:00-12:10', '14:50-18:23', '19:00-19:01']
            },
            {
                'courier_id': 2,
                'courier_type': 'bike',
                'regions': [1, 2, 3],
                'working_hours': ['11:00-11:50']
            },
            {
                'courier_id': 3,
                'courier_type': 'car',
                'regions': [2],
                'working_hours': ['10:00-18:00']
            }
        ]
    })
    assert response.status_code == 201
    assert response.json() == {'couriers': [{'id': 1}, {'id': 2}, {'id': 3}]}

    # проверяем с невалидными данными
    response = client.post('/couriers', json={
        'data': [
            {
                # такой айди уже существует
                'courier_id': 1,
                'courier_type': 'foot',
                'regions': [1, 2, 3],
                'working_hours': ['11:00-12:10', '14:50-18:23', '19:00-19:01']
            },
            {
                # такого типа курьера не существует
                'courier_id': 4,
                'courier_type': 'bla',
                'regions': [1, 2, 3],
                'working_hours': ['11:00-11:50']
            },
            {
                # не заданы регионы
                'courier_id': 5,
                'courier_type': 'car',
                'regions': [],
                'working_hours': ['10:00-18:00']
            },
            {
                # задано некорректное время работы
                'courier_id': 6,
                'courier_type': 'car',
                'regions': [1],
                'working_hours': ['10:00-27:00']
            },
            {
                # отсутствуют некоторые поля
                'courier_id': 7,
                'courier_type': 'car'
            },
            {
                # айди повторяется
                'courier_id': 8,
                'courier_type': 'car',
                'regions': [1],
                'working_hours': ['10:00-18:00']
            },
            {
                # айди повторяется
                'courier_id': 8,
                'courier_type': 'car',
                'regions': [1],
                'working_hours': ['10:00-18:00']
            },
            {
                # полностью валидный, его не должно быть в validation errors
                'courier_id': 9,
                'courier_type': 'car',
                'regions': [1, 100],
                'working_hours': ['10:00-18:00']
            }
        ]
    })
    assert response.status_code == 400
    assert response.json() == {'validation_error': {
        'couriers': [{'id': 1}, {'id': 4}, {'id': 5}, {'id': 6}, {'id': 7}, {'id': 8}, {'id': 8}]}
    }


def test_patch_couriers(client: TestClient, event_loop: asyncio.AbstractEventLoop):
    # меняем один параметр
    response = client.patch('/couriers/1', json={'regions': [1, 2, 3, 4]})
    assert response.status_code == 200
    assert response.json() == {
        'courier_id': 1,
        'courier_type': 'foot',
        'regions': [1, 2, 3, 4],
        'working_hours': ['11:00-12:10', '14:50-18:23', '19:00-19:01']
    }
    # меняем сразу несколько параметров
    response = client.patch('/couriers/2', json={'regions': [1, 2, 3, 4], 'courier_type': 'car'})
    assert response.status_code == 200
    assert response.json() == {
        'courier_id': 2,
        'courier_type': 'car',
        'regions': [1, 2, 3, 4],
        'working_hours': ['11:00-11:50']
    }
    # передаём неописанное поле
    response = client.patch('/couriers/2', json={'regions': []})
    assert response.status_code == 400
    # передаём невалидное поле
    response = client.patch('/couriers/2', json={'regions': ['sdf']})
    assert response.status_code == 422


def test_post_orders(client: TestClient, event_loop: asyncio.AbstractEventLoop):
    # проверяем, как сервер отреагирует на валидные данные
    response = client.post('/orders', json={
        'data': [
            {
                'order_id': 1,
                'weight': 0.23,
                'region': 1,
                'delivery_hours': ['10:00-14:20']
            },
            {
                'order_id': 2,
                'weight': 12,
                'region': 2,
                'delivery_hours': ['11:00-11:05']
            },
            {
                'order_id': 3,
                'weight': 0.01,
                'region': 1,
                'delivery_hours': ['17:50-18:00', '16:50-17:10']
            }
        ]
    })
    assert response.status_code == 201
    assert response.json() == {'orders': [{'id': 1}, {'id': 2}, {'id': 3}]}

    # проверяем с невалидными данными
    response = client.post('/orders', json={
        'data': [
            {
                # такой айди уже существует
                'order_id': 1,
                'weight': 1.05,
                'region': 1,
                'delivery_hours': ['11:00-12:10', '14:50-18:23', '19:00-19:01']
            },
            {
                # недопустимый вес
                'order_id': 4,
                'weight': 10000,
                'region': 1,
                'delivery_hours': ['11:00-11:50']
            },
            {
                # невалидный регион
                'order_id': 5,
                'weight': 1.05,
                'region': 'foo',
                'delivery_hours': ['10:00-18:00']
            },
            {
                # задано некорректное время доставки
                'order_id': 6,
                'weight': 1.05,
                'region': 1,
                'delivery_hours': ['10:00-27:00']
            },
            {
                # отсутствуют некоторые поля
                'order_id': 7,
                'weight': 1.05
            },
            {
                # айди повторяется
                'order_id': 8,
                'weight': 1.05,
                'region': 1,
                'delivery_hours': ['10:00-18:00']
            },
            {
                # айди повторяется
                'order_id': 8,
                'weight': 1.05,
                'region': 1,
                'delivery_hours': ['10:00-18:00']
            },
            {
                # полностью валидный, его не должно быть в validation errors
                'order_id': 9,
                'weight': 1.05,
                'region': 1,
                'delivery_hours': ['10:00-18:00']
            }
        ]
    })
    assert response.status_code == 400
    assert response.json() == {'validation_error': {
        'orders': [{'id': 1}, {'id': 4}, {'id': 5}, {'id': 6}, {'id': 7}, {'id': 8}, {'id': 8}]}
    }


def test_post_orders_assign(client: TestClient, event_loop: asyncio.AbstractEventLoop):
    # среди всех ранее созданных заказов для первого курьера подойдет только 1 и 3 заказы
    response = client.post('/orders/assign', json={
        'courier_id': 1
    })
    assert response.status_code == 200
    assign_time = response.json()['assign_time']
    assert response.json() == {'orders': [{'id': 1}, {'id': 3}], 'assign_time': assign_time}
    # добавляем ещё два заказа, которые подходят по всем параметрам, но которые нельзя назначить
    # из-за суммарного веса
    client.post('/orders', json={
        'data': [
            {
                'order_id': 4,
                'weight': 8.21,
                'region': 2,
                'delivery_hours': ['10:00-14:20']
            },
            {
                'order_id': 5,
                'weight': 9,
                'region': 2,
                'delivery_hours': ['07:00-11:00']
            }
        ]
    })
    response = client.post('/orders/assign', json={
        'courier_id': 1
    })
    assert response.status_code == 200
    assert response.json() == {'orders': [{'id': 1}, {'id': 3}, {'id': 4}], 'assign_time': assign_time}
    # выдадим заказы ещё одному курьеру, ему не должны достаться заказы первого курьера
    response = client.post('/orders/assign', json={
        'courier_id': 3
    })
    assign_time = response.json()['assign_time']
    assert response.status_code == 200
    assert response.json() == {'orders': [{'id': 2}, {'id': 5}], 'assign_time': assign_time}
    # не осталось свободных заказов, второму курьеру ничего не достанется
    response = client.post('/orders/assign', json={
        'courier_id': 2
    })
    assert response.status_code == 200
    assert response.json() == {'orders': []}
    # теперь изменяем третьего курьера, он не сможет доставить один заказ; этот заказ нужно отдать второму
    client.patch('/couriers/3', json={'courier_type': 'bike'})
    response = client.post('/orders/assign', json={
        'courier_id': 2
    })
    assign_time = response.json()['assign_time']
    assert response.status_code == 200
    assert response.json() == {'orders': [{'id': 5}], 'assign_time': assign_time}


def test_post_orders_complete(client: TestClient, event_loop: asyncio.AbstractEventLoop):
    # проверяем заказ, который назначен не тому курьеру
    response = client.post('/orders/complete', json={
        'courier_id': 2,
        'order_id': 1,
        'complete_time': (dt.datetime.utcnow() + dt.timedelta(seconds=300)).replace(tzinfo=None).isoformat()
    })
    assert response.status_code == 400
    # завершаем заказ в первом регионе через 300 секунд после назначения
    response = client.post('/orders/complete', json={
        'courier_id': 1,
        'order_id': 1,
        'complete_time': (dt.datetime.utcnow() + dt.timedelta(seconds=300)).replace(tzinfo=None).isoformat()
    })
    assert response.status_code == 200
    assert response.json() == {'order_id': 1}
    # завершаем заказ в первом регионе через 200 секунд после выполнения прошлого заказа (теперь t ср. - 250 секунд)
    client.post('/orders/complete', json={
        'courier_id': 1,
        'order_id': 3,
        'complete_time': (dt.datetime.utcnow() + dt.timedelta(seconds=500)).replace(tzinfo=None).isoformat()
    })
    # завершаем заказ во втором регионе через 400 секунд после выполнения прошлого заказа
    client.post('/orders/complete', json={
        'courier_id': 1,
        'order_id': 4,
        'complete_time': (dt.datetime.utcnow() + dt.timedelta(seconds=900)).replace(tzinfo=None).isoformat()
    })


def test_get_courier(client: TestClient, event_loop: asyncio.AbstractEventLoop):
    # по формуле рейтинг должен быть равен 4.65, а заработок за все время 3000
    response = client.get('/couriers/1')
    assert response.json() == {
        'courier_id': 1,
        'courier_type': 'foot',
        'regions': [1, 2, 3, 4],
        'working_hours': ['11:00-12:10', '14:50-18:23', '19:00-19:01'],
        'rating': 4.65,
        'earnings': 3000
    }
