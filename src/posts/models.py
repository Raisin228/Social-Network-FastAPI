from datetime import datetime

from fastapi_users_db_sqlalchemy import SQLAlchemyBaseUserTable
from sqlalchemy import String, Column, Integer, MetaData, TIMESTAMP, ForeignKey, Boolean, Table
from sqlalchemy.orm import declarative_base

metadata = MetaData()
Base = declarative_base(metadata=metadata)


# Таблица для постов в бд
news = Table(
    'news',
    metadata,
    Column('id', Integer, primary_key=True, nullable=False),
    Column('topic', String, nullable=True),
    Column('main_text', String, nullable=False),
    Column('image_url', String, nullable=False),
    Column('created_at', TIMESTAMP(timezone=True), default=datetime.utcnow, nullable=False),
    Column('updated_at', TIMESTAMP(timezone=True), nullable=True),
    Column('user_id', Integer, ForeignKey('user.id'), nullable=False)
)
