from django.urls import path
from .views import parent_pay_view, parent_payment_view, payment_success_view, payment_history_view, tutor_earnings_view

urlpatterns = [
    path("<int:pk>/", parent_pay_view, name="parent_pay_view"),
    path("<int:pk>/checkout/", parent_payment_view, name="parent_payment_view"),
    path("success/<int:pk>/", payment_success_view, name="payment_success_view"),
    path("history/", payment_history_view, name="parent_payment_history_view"), 
    path("earnings/", tutor_earnings_view, name="tutor_earnings_view")
]