from django.urls import path
from .views import signup_view, tutor_profile_create_view, login_view, logout_view

urlpatterns = [
    path('signup/', signup_view, name='signup'),
    path('tutor-profile-create/', tutor_profile_create_view, name='tutor_profile_create'),
    path('login/', login_view, name='login'),
    path('logout/', logout_view, name='logout'),
]