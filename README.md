Если порт занят службой то:  
netstat -ano | findstr :8080 - ищем процесс  
taskkill /PID <PID> /F - завершаем его
---
Запуск тестов -> `poetry run pytest tests/`  
Проверка кода на покрытие тестами -> `poetry run pytest --cov .`  
Преобразовать файлик .coverage в удобочитаемый отчёт -> `coverage html`
#78%



