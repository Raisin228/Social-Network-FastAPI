from application.news.models import News, NewsFiles
from data_access_object.base import BaseDAO


class NewsDao(BaseDAO):
    model = News


class NewsFilesDao(BaseDAO):
    model = NewsFiles
