from django.urls import path
from .views import register, login, logout, profile, CreateproductAPIView, SeedListingAPIView, ByproductListingAPIView

urlpatterns=[
    path("register/",register),
    path("login/",login),
    path("profile/",profile),
    path("logout/",logout),
    path("create/",CreateproductAPIView.as_view()),
    path("seed/",SeedListingAPIView.as_view()),
    path("byproduct/",ByproductListingAPIView.as_view()),
]