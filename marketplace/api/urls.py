from .views import register, login, logout, profile, CreateproductAPIView, SeedListingAPIView, ByproductListingAPIView, SeedMarketView, ByproductMarketView, BuyProductView
from django.urls import path

urlpatterns=[
    path("register/",register),
    path("login/",login),
    path("profile/",profile),
    path("logout/",logout),
    path("create/",CreateproductAPIView.as_view()),
    path("seed/",SeedListingAPIView.as_view()),
    path("byproduct/",ByproductListingAPIView.as_view()),
    path("market/seeds/",SeedMarketView.as_view()),
    path("market/byproducts/",ByproductMarketView.as_view()),
    path("buy/",BuyProductView.as_view()),
]