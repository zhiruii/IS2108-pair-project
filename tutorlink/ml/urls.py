from django.urls import path
from .views import price_suggestion_view

urlpatterns = [
    path('suggest-price/', price_suggestion_view, name='price_suggestion'),
]
