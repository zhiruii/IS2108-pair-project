from django.urls import path
from .views import parent_pay_view, parent_payment_view, payment_success_view, payment_history_view

urlpatterns = [
    path("parent-payment-page/<int:pk>/", parent_pay_view, name="parent_pay_view"),
    path("parent-payment-view/<int:pk>/", parent_payment_view, name="parent_payment_view"),
    path("payment-success-view/<int:pk>/", payment_success_view, name="payment_success_view"),
    path("payment-history-view/", payment_history_view, name="parent_payment_history_view")
]