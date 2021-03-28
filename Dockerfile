FROM tiangolo/uvicorn-gunicorn-fastapi:python3.8

COPY ./yandex-task /app
COPY ./yandex-task/requirements.txt requirements.txt
RUN pip3 install -r requirements.txt
