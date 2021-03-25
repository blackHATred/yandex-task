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
register_tortoise(
    app=app,
    db_url='sqlite://db.sqlite3',
    modules={'models': ['models.courier', 'models.order']},
    generate_schemas=True
)
app.include_router(router)

