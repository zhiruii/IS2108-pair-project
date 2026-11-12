from django.urls import path
from .views import (
    parent_listings_view,
    tutor_listings_view,
    create_listing_view,
    edit_listing_view,
    close_listing_view,
    tutor_public_profile_view
)

urlpatterns = [
    path("browse-listings/", parent_listings_view, name="parent_listings_view"),
    path("my-listings/", tutor_listings_view, name="tutor_listings_view"),
    path("create-listing/", create_listing_view, name="create_listing_view"),
    path("<int:pk>/edit/", edit_listing_view, name="edit_listing_view"),
    path("<int:pk>/close/", close_listing_view, name="close_listing_view"),
    path("tutor/<int:pk>/", tutor_public_profile_view, name="tutor_public_profile_view")
]
