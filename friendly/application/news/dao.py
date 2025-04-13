from application.news.models import News, NewsFiles, Reaction
from data_access_object.base import BaseDAO


class NewsDao(BaseDAO):
    model = News


class NewsFilesDao(BaseDAO):
    model = NewsFiles


class ReactionDao(BaseDAO):
    model = Reaction
