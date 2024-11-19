import asyncio
from json import loads
from os import listdir
from pathlib import Path
from typing import Dict, List

from application.storage.models import FileType
from database import get_async_session
from sqlalchemy import delete, insert

current_dir: Path = Path(__file__).parent
path_seed_data: Path = (current_dir / "../../seed_data").resolve()


def read_file(file_path: str) -> List[Dict]:
    """Прочитать данные из файла"""
    return loads(open(file_path, "r").read())


async def insert_data(fixtures: list, table_name: str) -> None:
    """<Вшиваем> стандартные данные в модель и удаляем предыдущие"""
    models = {"fileType": FileType}
    table = models.get(table_name)
    async for session in get_async_session():
        await session.execute(delete(table))
        for item in fixtures:
            await session.execute(insert(table).values(item))
        await session.commit()


def get_file_paths() -> List[str]:
    """Список файлов в директории"""
    return listdir(path_seed_data)


async def load_data_in_db():
    file_paths: list = get_file_paths()
    for file_path in file_paths:
        seeds: list = read_file(file_path=(path_seed_data / file_path).resolve())
        await insert_data(fixtures=seeds, table_name=file_path.removesuffix(".json"))


asyncio.run(load_data_in_db())

# TODO папка со скриптами должна бы быть в корне проекта а не рядом с исходниками
