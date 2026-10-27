from django.urls import path
from .views import parent_listings_view, tutor_listings_view

urlpatterns = [
    path("parent-view-listings/", parent_listings_view, name="parent_listing_view"),
    path("tutor-view-listings/", tutor_listings_view, name="tutor_listing_view"),
]
