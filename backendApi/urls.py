from django.urls import path
from . import views

app_name = 'api'

urlpatterns =[
    path('sec-urls', views.get_sec_files, name='securls')
]