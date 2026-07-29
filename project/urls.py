from django.urls import path
from . import views

urlpatterns = [
    path("", views.home, name="home"),
    path("reservation/create/", views.create_reservation, name="create_reservation"),
    path("reservation/<uuid:token>/", views.reservation_detail, name="reservation_detail"),
    path("check-hours/", views.check_working_hours, name="check_working_hours"),
]
