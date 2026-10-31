from django.urls import path
from .views import rate_package_view, my_ratings_view, dispute_rating_view, my_disputes_view

urlpatterns = [
    path('rate/<int:package_id>/', rate_package_view, name='rate_package'),
    path('my_ratings/', my_ratings_view, name='my_ratings'),
    path('dispute/<int:rating_id>/', dispute_rating_view, name='dispute_rating'),
    path('my_disputes/', my_disputes_view, name='my_disputes'),
]
