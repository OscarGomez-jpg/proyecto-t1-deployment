"""
Internal Request urls

This module defines URL patterns for the internal requests application.
"""

from django.urls import path

from apps.internalRequests import views

app_name = "internalRequests"

urlpatterns = [
    path("", views.show_requests, name="show_requests"),
    path("change-status/<int:id>", views.change_status, name="change_status"),
    path(
        "change-final-date/<int:id>", views.change_final_date, name="change_final_date"
    ),
    path(
        "assign-request/<int:request_id>", views.assign_request, name="assign_request"
    ),
    path("<int:id>/", views.detail_request, name="request_detail"),
    path(
        "show-traceability/<int:request_id>",
        views.show_traceability,
        name="show_traceability",
    ),
    path(
        "update-request/<int:request_id>", views.update_request, name="update_request"
    ),
    # Review paths
    path(
        "assign-request/<int:request_id>", views.assign_request, name="assign_request"
    ),
    path("<int:id>/", views.detail_request, name="request_detail"),
    path(
        "show-traceability/<int:request_id>",
        views.show_traceability,
        name="show_traceability",
    ),
]
