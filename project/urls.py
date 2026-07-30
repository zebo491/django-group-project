from django.urls import path
from django.contrib.auth import views as auth_views
from . import views
from .forms import StyledAuthenticationForm

urlpatterns = [
    path("", views.home, name="home"),
    path("reservation/create/", views.create_reservation, name="create_reservation"),
    path("reservation/<uuid:token>/", views.reservation_detail, name="reservation_detail"),
    path("check-hours/", views.check_working_hours, name="check_working_hours"),

    path("register/", views.register_view, name="register"),
    path("login/", auth_views.LoginView.as_view(
        template_name="login.html", authentication_form=StyledAuthenticationForm
    ), name="login"),
    path("logout/", auth_views.LogoutView.as_view(next_page="home"), name="logout"),
]
