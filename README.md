Если порт занят службой то:
netstat -ano | findstr :8080 - ищем процесс
taskkill /PID <PID> /F - завершаем его
---

