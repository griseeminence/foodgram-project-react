## Проект Foodgram

### **Описание проекта**:  

Сайт, на котором пользователи могут публиковать рецепты, 
добавлять чужие рецепты в избранное и подписываться на публикации
других авторов. Пользователям сайта также могут пользоваться сервисом
«Список покупок». Он позволит создавать и скачивать список продуктов,
которые нужно купить для приготовления выбранных блюд.

Проект доступен по [ссылке](https://foodgrabber.ddns.net/)

Суперпользователь:
```
email: admin@admin.com
password: admin
```

### **Технологии**:  

Python, Django, Django Rest Framework, Djoser, React, PostgreSQL, Docker, Nginx, Gunicorn 

### **Как запустить проект на сервере:**

- Клонировать репозиторий (локально):
```
https://github.com/griseeminence/foodgram-project-react.git
```

- Последовательно установить на сервер Docker, Docker Compose. Список команд:

```
sudo apt install curl
curl -fsSL https://get.docker.com -o get-docker.sh
sh get-docker.sh
sudo apt-get install docker-compose-plugin
```

- Создать на сервере папку foodgram и перейти в неё:

```
mkdir foodgram
cd foodgram
```

- Копировать в папку foodgram на сервере файлы docker-compose.yml, nginx.conf 
из папки infra локального проекта (при необходимости, укажите в файле docker-compose.yml ссылки на собственные образы:

- Создать в папке foodgram на сервере файл .env:

```
sudo touch .env
```

- Добавьте в файл .env личную информацию о БД (пример):

```
POSTGRES_USER=foodgram_user
POSTGRES_PASSWORD=foodgram_password
POSTGRES_DB=foodgram_db
DB_HOST=db
DB_PORT=5432
```

- Запустить контейнеры Docker (на сервере):

```
sudo docker compose up -d
```

- Создать миграции, создать суперпользователя, собрать статику:

```
sudo docker compose exec backend python manage.py makemigrations
sudo docker compose exec backend python manage.py migrate
sudo docker compose exec backend python manage.py collectstatic
sudo docker compose exec backend python manage.py createsuperuser
```

### **Лицензия**  
MIT License

Copyright (c) [2024] [Foodgram]

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

### **Автор**  
*Кольцов П.*

### **Контакты**
```
k.pavel080@gmail.com
```