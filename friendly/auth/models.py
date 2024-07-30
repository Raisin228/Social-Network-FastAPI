from sqlalchemy import Table, Column, Integer, String, MetaData

meta_data = MetaData()

user_table = Table(
    'user',
    meta_data,
    Column('id', Integer, primary_key=True, nullable=False),
    Column('first_name', String(100), nullable=True),
    Column('last_name', String(100), nullable=True),
    Column('username', String(100), nullable=False)
)

