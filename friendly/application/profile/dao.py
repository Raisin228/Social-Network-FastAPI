from application.auth.models import User
from data_access_object.base import BaseDAO


class ProfileDao(BaseDAO):
    model = User
