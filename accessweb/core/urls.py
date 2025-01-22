from django.urls import path, include
from core import views
urlpatterns = [
    path('', views.index, name='index'),
    path('login', views.Login, name='login'),
    path('register', views.Register, name='register'),
    path('logout', views.Logout, name='logout'),
]
