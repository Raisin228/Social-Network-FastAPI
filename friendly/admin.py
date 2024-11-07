from application.auth.models import User
from database import async_engine
from sqladmin import Admin, ModelView


class UserAdmin(ModelView, model=User):
    icon = "fa-solid fa-user"

    can_create = True
    can_edit = True
    can_delete = True
    can_view_details = True
    can_export = False

    column_list = [User.id, User.nickname, User.email]

    column_searchable_list = [User.email]
    column_sortable_list = [User.id, User.email]
    column_default_sort = [(User.email, False)]

    column_details_exclude_list = [User.password]

    page_size = 25
    page_size_options = [25, 50, 100, 200]


def setup_admin(application):
    """Связываем админку с приложением"""
    admin = Admin(
        application, async_engine, title="Friendly Administration", favicon_url="/static/images/admin_favicon.png"
    )
    admin.add_view(UserAdmin)
