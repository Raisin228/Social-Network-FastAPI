import os
import sys

from fastapi import FastAPI
from database import create_tables, insert_data

sys.path.insert(1, os.path.join(sys.path[0], '..'))

app = FastAPI()

create_tables()
insert_data()
