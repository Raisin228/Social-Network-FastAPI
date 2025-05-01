import asyncio
import os
import sys
from json import loads
from os import listdir
from pathlib import Path
from typing import Dict, List

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../")))
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../friendly/")))

from database import Base, get_async_session  # noqa
from sqlalchemy import delete, insert  # noqa

from friendly.application.news.dao import ReactionDao  # noqa
from friendly.application.storage.dao import FileTypeDao  # noqa

current_dir: Path = Path(__file__).parent
path_seed_data: Path = (current_dir / "../seed_data").resolve()


def read_file(file_path: str) -> List[Dict]:
    """Прочитать данные из файла"""
    return loads(open(file_path, "r").read())


async def insert_data(fixtures: list, table_name: str) -> None:
    """<Вшиваем> стандартные данные в модель и удаляем предыдущие"""
    models = {"fileType": FileTypeDao, "reaction": ReactionDao}
    table_dao = models.get(table_name)
    async for session in get_async_session():
        await table_dao.delete_by_filter(session, {})
        for item in fixtures:
            await table_dao.add(session, item)
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
