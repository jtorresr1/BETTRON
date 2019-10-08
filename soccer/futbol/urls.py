from django.urls import path
from futbol.views import *

app_name = 'futbolmod'

urlpatterns = [
    path('',index,name="index"),
    path('actualizar/',actualizar,name="actualizar"),
    path('success/',simple_upload,name="upload"),
    path('add_team/',add_team,name="add_equipo"),
    path('add_league/',add_league,name="add_liga"),
]
