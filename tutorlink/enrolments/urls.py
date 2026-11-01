from django.urls import path
from .views import (
    send_enrolment_request_view,
    parent_my_requests_view,
    parent_withdraw_request_view,
    tutor_requests_view,
    tutor_accept_request_view,
    tutor_decline_request_view,
    parent_view_my_lessons
)

urlpatterns = [
    path(
        "send_enrolment_request/<int:pk>/",
        send_enrolment_request_view,
        name="send_enrolment_request_view",
    ),
    path(
        "parent_my_requests_view/",
        parent_my_requests_view,
        name="parent_my_requests_view",
    ),
    path(
        "parent_withdraw_request_view/<int:pk>/",
        parent_withdraw_request_view,
        name="parent_withdraw_request_view",
    ),
    path("tutor_requests_view/", tutor_requests_view, name="tutor_requests_view"),
    path(
        "tutor_accept_request_view/<int:pk>/",
        tutor_accept_request_view,
        name="tutor_accept_request_view",
    ),
    path(
        "tutor_decline_request_view/<int:pk>/",
        tutor_decline_request_view,
        name="tutor_decline_request_view",
    ),
    path(
        "my-lessons/",
        parent_view_my_lessons,
        name="parent_view_my_lessons"
    )
]
