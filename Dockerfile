FROM python:3.8-alpine

RUN apk add --no-cache sqlite

WORKDIR /usr/src/app

COPY requirements.txt ./

RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 80:8000

CMD ["python", "manage.py runserver 0.0.0.0:8000"]