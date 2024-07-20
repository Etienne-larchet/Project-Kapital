from django.urls import path
from . import views

app_name = 'api'

urlpatterns =[
    path('sec-urls/', views.get_sec_files, name='securls'),
    path('update-t212/', views.update_t212, name='upt212')
]