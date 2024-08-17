from django.http import HttpResponseNotFound
from django.urls import include, path

urlpatterns = [
    path("api/", include("backendApi.urls")),
    path("login/", include("user.urls")),
    path("favicon.ico", lambda request: HttpResponseNotFound()),
]
