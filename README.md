## Проект «Foodgram»

### Описание
«Продуктовый помощник» — это онлайн-сервис, где пользователи могут публиковать рецепты, подписываться на публикации других пользователей, добавлять понравившиеся рецепты в список «Избранное», а перед походом в магазин скачивать полный список продуктов, необходимых для приготовления выбранных блюд.

### Технологии
Python 3.8, Django 3.2, DRF 3.12, Docker, Nginx

<details>
<summary><h3>Как запустить проект</h3></summary>

- Клонировать репозиторий и перейти в директорию для развертывания:

```
git clone git@github.com:Sergey-python/foodgram-project-react.git
```

```
cd foodgram-project-react/infra/
```

- Переменные окружения, используемые в проекте(для этого создайте и заполните файл .env):

```
DB_ENGINE=django.db.backends.postgresql # указываем, что работаем с postgresql
DB_NAME=postgres # имя базы данных
POSTGRES_USER=postgres # логин для подключения к базе данных
POSTGRES_PASSWORD=postgres # пароль для подключения к БД (установите свой)
DB_HOST=db # название сервиса (контейнера)
DB_PORT=5432 # порт
```

- Чтобы развернуть проект выполните команду:

```
docker-compose up -d
```

- Затем следует сделать миграции и собрать статику.

```
docker-compose exec web python manage.py migrate
docker-compose exec web python manage.py collectstatic --no-input
```

- Остановка проекта осуществляется командой.

```
docker-compose stop
```

</details>

### Примеры запросов к API
Примеры запросов доступны в документации по адресу http://127.0.0.1/redoc/ после запуска проекта.
