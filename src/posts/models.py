from datetime import datetime

from sqlalchemy import String, Column, Integer, MetaData, TIMESTAMP, ForeignKey, Table
from sqlalchemy.orm import declarative_base

metadata = MetaData()
Base = declarative_base(metadata=metadata)

# table posts in db
news = Table(
    'news',
    metadata,
    Column('id', Integer, primary_key=True, nullable=False),
    Column('topic', String, nullable=True),
    Column('main_text', String, nullable=False),
    Column('image_url', String, nullable=False),
    Column('quantity_like', Integer, nullable=False, default=0),
    Column('created_at', TIMESTAMP(timezone=True), default=datetime.utcnow, nullable=False),
    Column('updated_at', TIMESTAMP(timezone=True), nullable=True),
    Column('user_id', Integer, ForeignKey('user.c.id'), nullable=False)
)

# table liked posts in db
liked_posts = Table(
    'liked_posts',
    metadata,
    Column('id', Integer, primary_key=True, nullable=False),
    Column('user_id', Integer, ForeignKey('user.c.id'), nullable=False),
    Column('post_id', Integer, ForeignKey('news.id'), nullable=False)
)
