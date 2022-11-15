# podcasts/urls.py

from django.urls import path

from .views import HomePageView

urlpatterns = [
    path("podcasts", HomePageView.as_view(), name="homepage"),
]