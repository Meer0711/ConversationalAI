FROM python:3.12.2
ARG PROXY_HOST
ENV PYTHONUNBUFFERED 1
ENV PYTHONDONTWRITEBYTECODE 1

COPY . /app

WORKDIR /app

RUN ls -la

RUN sed -i 's/\r$//g' ./start_app.sh
RUN chmod +x ./start_app.sh

RUN sed -i 's/\r$//g' ./start_celery_worker.sh
RUN chmod +x ./start_celery_worker.sh

RUN sed -i 's/\r$//g' ./start_celery_flower.sh
RUN chmod +x ./start_celery_flower.sh

RUN pip install -r requirements.txt
