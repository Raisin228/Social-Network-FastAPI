from sqlalchemy import create_engine, text, insert
from config import settings
from friendly.auth.models import meta_data, user_table

sync_engine = create_engine(
    url=settings.db_url_psycopg,
    echo=True,
    pool_size=5,
    max_overflow=10
)


def create_tables():
    sync_engine.echo = False
    meta_data.drop_all(sync_engine)
    meta_data.create_all(sync_engine)
    sync_engine.echo = True


def insert_data():
    with sync_engine.connect() as conn:
        # запрос через orm
        stmt = insert(user_table).values([
            {'first_name': 'Alice',
             'last_name': 'Jon-con',
             'username': 'alice_123'
             }
        ])
        # запрос на sql
        # stmt = """INSERT INTO "user" (first_name, last_name, username) VALUES ('Alice', 'Jon-con', 'alice_123');"""
        conn.execute(stmt)
        conn.commit()
