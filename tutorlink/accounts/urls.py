from django.urls import path
from .views import signup_view, tutor_profile_create_view, login_view, logout_view, child_list_view, child_create_view, child_edit_view, child_delete_view

urlpatterns = [
    path('signup/', signup_view, name='signup'),
    path('tutor-profile-create/', tutor_profile_create_view, name='tutor_profile_create'),
    path('login/', login_view, name='login'),
    path('logout/', logout_view, name='logout'),
    path('children/', child_list_view, name='child_list'),
    path('children/add/', child_create_view, name='child_create'),
    path('children/<int:child_id>/edit/', child_edit_view, name='child_edit'),
    path('children/<int:child_id>/delete/', child_delete_view, name='child_delete'),

]