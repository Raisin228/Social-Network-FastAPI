import os

from pydantic_settings import BaseSettings, SettingsConfigDict

DOTENV = os.path.join(os.path.dirname(__file__), "../.env")


class Settings(BaseSettings):
    DB_HOST: str
    DB_PORT: int
    DB_USER: str
    DB_PASS: str
    DB_NAME: str
    TEST_DB_NAME: str = ""
    SECRET_KEY: str
    ALGORITHM: str

    @property
    def db_url_asyncpg(self):
        """DSN основной базы данных"""
        return f'postgresql+asyncpg://{self.DB_USER}:{self.DB_PASS}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}'

    @property
    def db_url_for_test(self):
        """DSN тестовой базы данных"""
        return f'postgresql+asyncpg://{self.DB_USER}:{self.DB_PASS}@{self.DB_HOST}:{self.DB_PORT}/{self.TEST_DB_NAME}'

    @property
    def auth_data(self):
        return {'secret_key': self.SECRET_KEY, 'algorithm': self.ALGORITHM}

    model_config = SettingsConfigDict(env_file=DOTENV)


settings = Settings()
