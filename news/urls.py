from django.urls import path

from .views import HomePageView

urlpatterns = [
    path("news", HomePageView.as_view(), name="home"),
]