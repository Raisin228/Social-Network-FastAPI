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
Запуск тестов -> `poetry run pytest tests/`  
Проверка кода на покрытие тестами -> `poetry run pytest --cov .`  
Преобразовать файлик .coverage в удобочитаемый отчёт -> `coverage html`  
---  
Запуск pre-commit
`pre-commit run -a`

Вшить стандартные данные в DB  
`python .\scripts\load_values_db.py`

Запуск Celery Worker (cd friendly)
`celery -A task_queue.__init__:celery worker --loglevel=INFO --pool=solo`
Запуск Flower
`celery -A task_queue.__init__:celery flower --address=127.0.0.1 --port=5555`


Сейчас фокус на постах пользователей.
Личная страница пользователя с постами посты как отдельный модуль с поддержкой характеристик количество лайков 
комментарий количество репостов просмотров содержательную информации текст фото музыка файлы

