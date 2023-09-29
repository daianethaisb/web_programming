from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),
    path("createAuction", views.createAuction, name="createAuction"),
    path("viewAuction/<int:auction_id>", views.viewAuction, name="viewAuction"),
    path("watchlist", views.watchlist, name="watchlist"),
    path("categories", views.categories, name="categories"),
    path("categoryList/<int:category_id>", views.categoryList, name="categoryList"),
    path("bid", views.bid, name="bid"),
    path("closeAuction/<str:auction_id>", views.closeAuction, name="closeAuction"),
    path("comment/<str:auction_id>", views.comment, name="comment")
]
