from django.urls import path, include
from . import views

urlpatterns = [
    path(
        '',
        views.index,
        name='browse'
    ),
    path(
        'start_session/<str:user_id>/<str:screen_dex>/',
        views.start_session, 
        name=''
    ),
    path(
        'getcookkie/', 
        views.getCookie, 
        name=''
    ),
]
