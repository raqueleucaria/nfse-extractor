from django.urls import path
from . import views

app_name = 'extractor'

urlpatterns = [
    path('', views.index, name='index'),
    path('api/hello/', views.hello_api, name='hello_api'),
]

