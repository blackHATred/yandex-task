# Решение задачи от Яндекса
После развёртки протестировать API можно в `/docs` и `/redoc` (если не заданы
переменные окружения `DOCS_URL` и `REDOC_URL`)

## Инструкция по развёртке
Самый простой способ - следовать официальной инструкции к фреймворку fastapi: https://fastapi.tiangolo.com/deployment/docker/
1) `git clone https://github.com/blackHATred/yandex-task`
2) `cd yandex-task`
3) `sudo docker build -t (*название образа*) .`
4) `sudo docker run -d --name (*имя контейнера*) -p 80:80 (*название образа*)`
* В рамках задачи последняя команда была подкорректирована: `sudo docker run --restart-always -d --name mycontainer -p 8080:80 myimage`. Это сделано с целью добавления приложения в автозагрузку и использования 8080 порта

## Конфигурация
1) задать ссылки для просмотра API можно через переменные окружения DOCS_URL и REDOC_URL (подробнее про генерацию документации API см. здесь: https://fastapi.tiangolo.com/features/#automatic-docs)
2) по умолчанию проект использует БД sqlite, по желанию можно
использовать MySQL \ Postgres. Для этого нужно установить соответствующую СУБД и задать переменные окружения: 
* `DB` - используемая СУБД. Пример: `postgres` 
* `DB_USER` - имя пользователя. Пример: `user` 
* `DB_PASSWORD` - пароль. Пример: `mypassword`
* `DB_HOSTNAME` - хост. Пример: `localhost`
* `DB_PORT` - порт для подключения к БД. Пример: `5432` 
* `DB_NAME` - название БД. Пример: `name`. 
* В конечном итоге приложение будет подключаться к БД по `postgres://user:mypassword@localhost:5432/name`

## Тестирование
Запуск тестов происходит через команду `pytest -vv` в директории с **test_main.py**

## Зависимости
**fastapi** - основной фрейморк  
**pydantic** - валидация/создание/изменение моделей  
**tortoise-orm** - для работы с популярными СУБД  
**pytest** - тестирование  
**asynctest** - для поддержки fastapi и tortoise в тестах, т.к. они асинхронные  
**uvicorn и gunicorn** - внутренний сервер


## Примечания
* В **pytest.ini** выставлено игнорирование некоторых предупреждений ввиду
того, что с версии **python 3.7** вместо **@coroutine** используется **async def**, однако
некоторые библиотеки в проекте используют именно **@coroutine** (**DeprecationWarning** и как следствие **RuntimeWarning**)
* В рамках условия задачи проект был развёрнут не на **80**, а на **8080** порте



* утка  
````  
  __  
<(o )___            -кря?
 ( ._> /  
  `---'``
