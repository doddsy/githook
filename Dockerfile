FROM python:3.6-alpine

WORKDIR /app

RUN pip install Flask requests

COPY . .

ENV PORT=5000

EXPOSE ${PORT}

CMD ["python", "./app.py" ]