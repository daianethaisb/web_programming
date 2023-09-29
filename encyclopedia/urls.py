from django.urls import path

from . import views

app_name = "encyclopedia"
urlpatterns = [
    path("", views.index, name="index"),
    path("wiki/<str:title>", views.page, name="page"),
    path("search/", views.search, name="search"),
    path("create", views.createPage, name="createPage"),
    path("wiki/edit/<str:title>", views.editPage, name="editPage"),
    path("randompage", views.randomPage, name="randomPage")
]
