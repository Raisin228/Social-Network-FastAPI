FROM python:3.13.3-bookworm

ENV PYTHONBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

WORKDIR /app

RUN pip install --upgrade pip wheel "poetry==2.1.1"

RUN poetry config virtualenvs.create false --local

COPY pyproject.toml poetry.lock ./

RUN poetry install --no-root

COPY . .

RUN chmod +x prestart.sh

WORKDIR /app/friendly

ENTRYPOINT ["../prestart.sh"]

CMD ["python", "main.py"]