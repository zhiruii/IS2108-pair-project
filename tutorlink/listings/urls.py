from django.urls import path
from .views import parent_listings_view, tutor_listings_view, create_listing_view

urlpatterns = [
    path("parent-view-listings/", parent_listings_view, name="parent_listings_view"),
    path("tutor-view-listings/", tutor_listings_view, name="tutor_listings_view"),
    path("create-listing/", create_listing_view, name="create_listing_view"),
]
