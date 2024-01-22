FROM python:3.9

WORKDIR /app

RUN python -m pip install --upgrade pip
RUN pip install gunicorn

COPY requirements.txt .

RUN pip3 install -r requirements.txt --no-cache-dir

COPY . .

CMD ["gunicorn", "backend.wsgi", "--bind", "0:7000"]