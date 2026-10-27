from django.urls import path
from .views import send_enrolment_request_view

urlpatterns = [
    path("send_enrolment_request/<int:pk>/", send_enrolment_request_view, name='send_enrolment_request_view'),
]