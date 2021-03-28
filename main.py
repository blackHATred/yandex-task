from fastapi import FastAPI
import os
from tortoise.contrib.fastapi import register_tortoise

from routes import router

app = FastAPI(
    title='Сласти от всех напастей',
    description='Решение для задания второго этапа',
    version='1.0.0',
    docs_url=os.getenv('DOCS_URL', '/docs'),
    redoc_url=os.getenv('REDOC_URL', '/redoc'),
)

print('i`m working!')
DB = os.getenv('DB', False)
DB_USER = os.getenv('DB_USER', '')
DB_PASSWORD = os.getenv('DB_PASSWORD', '')
DB_HOSTNAME = os.getenv('DB_HOSTNAME', '')
DB_PORT = os.getenv('DB_PORT', '')
DB_NAME = os.getenv('DB_NAME', '')

register_tortoise(
    app=app,
    db_url=f'{DB}://{DB_USER}:{DB_PASSWORD}@{DB_HOSTNAME}:{DB_PORT}/{DB_NAME}' if DB else 'sqlite://db.sqlite',
    # db_url=f'{DB}://{DB_USER}:{DB_PASSWORD}@{DB_HOSTNAME}:{DB_PORT}/{DB_NAME}' if DB else 'sqlite://:memory:',
    modules={'models': ['models.courier', 'models.order']},
    generate_schemas=True
)
app.include_router(router)
