from django.urls import path
from .views import parent_pay_view

urlpatterns = [
    path("parent-payment-page/<int:pk>/", parent_pay_view, name="parent_pay_view"),
]