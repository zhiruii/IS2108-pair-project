from django.urls import path
from .views import rate_package_view, my_ratings_view

urlpatterns = [
    path('rate/<int:package_id>/', rate_package_view, name='rate_package'),
    path('my_ratings/', my_ratings_view, name='my_ratings'),
]
