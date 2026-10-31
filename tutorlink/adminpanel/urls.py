from django.urls import path
from .views import admin_home_view, user_list_view, user_edit_view, user_delete_view, rating_delete_view, rating_list_view, dispute_list_view, dispute_resolve_view
urlpatterns = [
    path('', admin_home_view, name='admin_home'),
    path('users/', user_list_view, name='admin_user_list'),
    path('user/<int:user_id>/edit/', user_edit_view, name='admin_user_edit'),
    path('user/<int:user_id>/delete/', user_delete_view, name='admin_user_delete'),
    path('ratings/', rating_list_view, name='admin_rating_list'),
    path('ratings/<int:rating_id>/delete/', rating_delete_view, name='admin_rating_delete'),
    path('disputes/', dispute_list_view, name='admin_dispute_list'),
    path('disputes/<int:dispute_id>/resolve/', dispute_resolve_view, name='admin_dispute_resolve'),

]