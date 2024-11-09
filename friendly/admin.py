from application.auth.dao import UserDao
from application.auth.models import User
from application.friends.models import Friend
from auth.hashing_password import hash_password
from database import async_engine, get_async_session
from sqladmin import Admin, ModelView
from wtforms import SelectField
from wtforms.validators import Email, Length


class BaseView(ModelView):
    page_size = 25
    page_size_options = [25, 50, 100, 200]
    can_export = False


class UserAdmin(BaseView, model=User):
    icon = "fa-solid fa-user"

    column_list = [User.id, User.nickname, User.email]
    column_searchable_list = [User.email]
    column_sortable_list = [User.id, User.email]
    column_default_sort = [(User.email, False)]
    column_details_exclude_list = [User.password]

    form_create_rules = ["first_name", "last_name", "birthday", "sex", "nickname", "email", "password"]
    form_edit_rules = ["first_name", "last_name", "birthday", "sex", "nickname", "email"]

    form_overrides = {"sex": SelectField}

    form_choices = {"sex": [("Male", "Male"), ("Female", "Female")]}

    form_args = {
        "sex": {
            "label": "Gender",
            "choices": [("Male", "Male"), ("Female", "Female")],
        },
        "email": {
            "validators": [Email(message="Invalid email address."), Length(max=100)],
        },
    }

    async def after_model_change(self, form, model, is_created, request):
        """После сохранения в бд. Хэшируем пароль"""
        if model.password and len(model.password) != 60:
            model.password = hash_password(model.password)

        async for session in get_async_session():
            await UserDao.update_row(session, model.to_dict(), {"id": model.id})


class FriendAdmin(BaseView, model=Friend):
    icon = "fa-duotone fa-solid fa-handshake"

    column_list = [Friend.user_id, Friend.friend_id]
    column_labels = {Friend.user_id: "Initiator relationship", Friend.friend_id: "Friendship receiver"}
    column_searchable_list = [Friend.user_id, Friend.friend_id]


def setup_admin(application):
    """Связываем админку с приложением"""
    admin = Admin(
        application, async_engine, title="Friendly Administration", favicon_url="/static/images/emblem_logo.png"
    )
    admin.add_view(UserAdmin)
    admin.add_view(FriendAdmin)
