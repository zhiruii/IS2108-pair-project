from django.urls import path
from .views import price_suggestion_view, price_review_view, price_flag_view, price_unflag_view


urlpatterns = [
    path('suggest-price/', price_suggestion_view, name='price_suggestion'),
    path('price-review/', price_review_view, name='price_review'),
    path('price-review/<int:listing_id>/flag/', price_flag_view, name='price_flag'),
    path('price-review/<int:listing_id>/unflag/', price_unflag_view, name='price_unflag'),
]
