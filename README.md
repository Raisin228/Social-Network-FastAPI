Для запуска БД:  
`brew services start postgresql@17`  

Для остановки БД:  
`brew services stop postgresql@17`

Создать новую миграцию:  
`alembic revision --autogenerate`

Если порт занят службой то:  Windows
`netstat -ano | findstr :8080` - ищем процесс  
`taskkill /PID <PID> /F` - завершаем его

`lsof -i :<PID>` - смотрим какие процессы зажали порт
`kill -9 <PID>` - убиваем процесс
---
Запуск тестов (cd friendly) -> `poetry run pytest ../tests/`  
Проверка кода на покрытие тестами (нужно выйти в корень) -> `poetry run pytest --cov .`  
Преобразовать файлик .coverage в удобочитаемый отчёт -> `coverage html`  
---  
Запуск pre-commit
`pre-commit run -a`

Вшить стандартные данные в DB  
`python ./scripts/load_values_db.py`

Запуск Celery Worker (cd friendly)
`celery -A task_queue.__init__:celery worker --loglevel=INFO --pool=solo`
Запуск Flower
`celery -A task_queue.__init__:celery flower --address=127.0.0.1 --port=5555`

Сборка FastAPI приложения   
`docker build . -t friendly`  
Запуск контейнера  (файл .env будет лежать на сервере)
`docker run --env-file .env -p 5050:8000 -it friendly`

Сейчас фокус на постах пользователей.
Личная страница пользователя с постами посты как отдельный модуль с поддержкой характеристик количество лайков 
комментарий количество репостов просмотров содержательную информации текст фото музыка файлы


запуск celery в docker?
запуск тестов в докер?

