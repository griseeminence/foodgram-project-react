FROM python:3.8-slim

WORKDIR /code

RUN python -m pip install --upgrade pip
RUN pip install gunicorn

COPY requirements.txt .

RUN pip3 install -r requirements.txt --no-cache-dir

COPY . .

CMD ["gunicorn", "backend.wsgi:application", "--bind", "0:7000"]