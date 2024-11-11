from typing import List, Type

from application.auth.dao import UserDao
from application.auth.models import User
from application.friends.models import Friend, Relations
from application.notifications.models import (
    FirebaseDeviceToken,
    Notification,
    NotificationStatus,
)
from auth.hashing_password import hash_password
from database import async_engine, get_async_session
from firebase.notification import NotificationEvent
from sqladmin import Admin, ModelView
from starlette.requests import Request
from wtforms import Form, SelectField, StringField
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

    form_args = {
        "sex": {
            "label": "Gender",
            "choices": [("Male", "Male"), ("Female", "Female")],
        },
        "email": {
            "validators": [Email(message="Invalid email address."), Length(max=100)],
        },
    }

    async def after_model_change(self, form, model, is_created, request) -> None:
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
    column_sortable_list = [Friend.user_id, Friend.friend_id]
    column_default_sort = [(Friend.user_id, False)]

    form_overrides = {"relationship_type": SelectField}

    form_args = {
        "relationship_type": {
            "label": "Relationship Type",
            "choices": [
                (Relations.FRIEND, Relations.FRIEND),
                (Relations.NOT_APPROVE, Relations.NOT_APPROVE),
                (Relations.BLOCKED, Relations.BLOCKED),
            ],
        }
    }

    async def scaffold_form(self, rules: List[str] | None = None) -> Type[Form]:
        """Отключаем QuerySelectField для внешних ключей"""
        form = await super().scaffold_form()
        form.user_id = StringField("Initiator Relationship ID", render_kw={"class": "form-control", "maxlength": "36"})
        form.friend_id = StringField("Friendship Receiver ID", render_kw={"class": "form-control", "maxlength": "36"})
        return form


class FirebaseDeviceTokenAdmin(BaseView, model=FirebaseDeviceToken):
    icon = "fa-solid fa-laptop"

    column_list = [FirebaseDeviceToken.holder_id, FirebaseDeviceToken.device_token]
    column_labels = {
        FirebaseDeviceToken.holder_id: "Token owner",
        FirebaseDeviceToken.device_token: "Device (FCM token)",
    }
    column_searchable_list = [FirebaseDeviceToken.holder_id]
    column_sortable_list = [FirebaseDeviceToken.holder_id]
    column_default_sort = [(FirebaseDeviceToken.holder_id, False)]

    column_formatters = {FirebaseDeviceToken.device_token: lambda t, a: t.device_token[:70] + "..."}

    async def scaffold_form(self, rules: List[str] | None = None) -> Type[Form]:
        """Переопределяем FK на StringField"""
        form = await super().scaffold_form()
        form.holder_id = StringField("Token owner ID", render_kw={"class": "form-control", "maxlength": "36"})
        return form


class NotificationAdmin(BaseView, model=Notification):
    icon = "fa-regular fa-bell"

    column_list = [Notification.sender, Notification.recipient, Notification.title]
    column_labels = {Notification.sender: "Sender", Notification.recipient: "Recipient", Notification.title: "Title"}
    column_searchable_list = [Notification.sender, Notification.recipient, Notification.title]
    column_sortable_list = [Notification.title]
    column_default_sort = [(Notification.title, False)]

    form_create_rules = ["title", "status", "created_at", "sender", "recipient"]

    form_overrides = {"title": SelectField, "status": SelectField}

    form_args = {
        "title": {"label": "Notification header", "choices": [(i.value, i.value) for i in NotificationEvent]},
        "status": {
            "label": "Message status",
            "choices": [
                (NotificationStatus.UNREAD, NotificationStatus.UNREAD),
                (NotificationStatus.READ, NotificationStatus.READ),
            ],
        },
    }

    def is_visible(self, request: Request) -> bool:
        return False

    async def scaffold_form(self, rules: List[str] | None = None) -> Type[Form]:
        """Добавляем Sender / Recipient в create форму"""
        form = await super().scaffold_form()
        form.sender = StringField("Sender ID", render_kw={"class": "form-control", "maxlength": "36"})
        form.recipient = StringField("Recipient ID", render_kw={"class": "form-control", "maxlength": "36"})
        return form


def setup_admin(application):
    """Связываем админку с приложением"""
    admin = Admin(
        application, async_engine, title="Friendly Administration", favicon_url="/static/images/emblem_logo.png"
    )
    admin.add_view(UserAdmin)
    admin.add_view(FriendAdmin)
    admin.add_view(FirebaseDeviceTokenAdmin)
    admin.add_view(NotificationAdmin)
