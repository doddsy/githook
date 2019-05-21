FROM python:3.6-alpine

MAINTAINER doddsy "hello@metrono.de"

WORKDIR /app

COPY ./configexample.py ./config.py

RUN pip install Flask requests

COPY . .

EXPOSE 5000

CMD ["python", "./app.py" ]