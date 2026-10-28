from django.urls import path
from .views import parent_listings_view, tutor_listings_view, create_listing_view, edit_listing_view, close_listing_view

urlpatterns = [
    path("parent-view-listings/", parent_listings_view, name="parent_listings_view"),
    path("tutor-view-listings/", tutor_listings_view, name="tutor_listings_view"),
    path("create-listing/", create_listing_view, name="create_listing_view"),
    path("edit-listing/<int:pk>/", edit_listing_view, name="edit_listing_view"),
    path("close-listing/<int:pk>/", close_listing_view, name="close_listing_view"),
]
