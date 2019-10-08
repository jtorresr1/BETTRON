from django.urls import path
from soccer.views import *

app_name = 'futbol'

urlpatterns = [
    path('', index, name="index"),
    path('apuestas/', apuestas, name="apuestas"),
    path('app_down/', formulario_general, name="form_general"),
    path('error', error, name="error"),
    path('add_matches/', add_matches, name="add_matches"),
    path('add_teams/', add_teams, name="add_teams"),
    path('add_ligas/', add_ligas, name="add_ligas"),
    path('newmatch/', newmatch, name="newmatch"),
    path('actualizar_ligas/', actualizar_matches, name ="actualizar_matches"),
    path('match_all/', match_all, name="match_all"),
    path('general/', general, name="general"),
    path('download/', download_pdfs, name="download_pdfs"),
]
