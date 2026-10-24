from django.urls import path
from .views import admin_home_view, user_list_view, user_edit_view
urlpatterns = [
    path('', admin_home_view, name='admin_home'),
    path('users/', user_list_view, name='admin_user_list'),
    path('user/<int:user_id>edit', user_edit_view, name='admin_user_edit')
]