import json
from django import forms
from .models import *

class RegPais(forms.ModelForm):

    Nac = []
    leagues = []
    p1 = {}
    for league in Ligas.objects.all():
        if (league.Nacion, league.Nacion) not in Nac:
            Nac.append((league.Nacion, league.Nacion))
        leagues.append((league.Liga, league.Liga))

        if league.Nacion in p1:
            p1[league.Nacion].append(league.Liga)
        else:
            p1[league.Nacion] = [league.Liga]
    """
    equipos = []
    for team in Equipos.objects.all():
        equipos.append((team.Nombre_Equipo,team.Nombre_Equipo))

    equipos = sorted(equipos)
    """
    Nac = sorted(Nac)
    leagues = sorted(leagues)
    Nacion = forms.ChoiceField(choices=(Nac))
    Liga = forms.ChoiceField(choices=())
    ligas = json.dumps(p1)

    class Meta:
        model = Partidos
        fields = ['Nacion', 'Liga', 'HomeTeam', 'AwayTeam']


class Checking(forms.ModelForm):
    Nacion = forms.CharField()
    Liga = forms.CharField()
    class Meta:
        model = Partidos
        fields = ['Nacion', 'Liga', 'HomeTeam', 'AwayTeam']