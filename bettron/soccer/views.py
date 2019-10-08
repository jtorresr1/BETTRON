from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.db.models import Count
import csv
from soccer.models import Ligas,Partidos,Equipos
from soccer.forms import *
from soccer.utils import *
import os
import time
from datetime import datetime,timedelta
from django.template.loader import get_template
from selenium import webdriver

def index(request):
    return render(request, 'soccer/index.html')

def error(request):
    return render(request,'soccer/error.html')


def apuestas(request):
    context = {}
    if request.method == 'POST':
        Nacion = request.POST['Nacion']
        league = request.POST['Liga']
        HomeTeam = request.POST['HomeTeam']
        AwayTeam = request.POST['AwayTeam']

        if Equipos.objects.filter(Nombre_Equipo=HomeTeam).count() != 1 or Equipos.objects.filter(
                Nombre_Equipo=AwayTeam).count() != 1:
            return redirect('futbol:error')

        probabilidadlocal, probabilidadvisita = promedio_goles(Nacion, league, HomeTeam, AwayTeam)
        if probabilidadlocal == 0:
            return HttpResponse("no tiene partidos previos para evaluar")

        evaluaciongoles = 8
        probloc, probvis = probabilidad_goles(probabilidadlocal, probabilidadvisita, evaluaciongoles)

        context = context_goles(evaluaciongoles, probloc, probvis)
        context['local_team'] = HomeTeam
        context['away_team'] = AwayTeam
        context['local'] = probloc
        context['visita'] = probvis

        return render(request, 'soccer/result.html', context)

    else:
        league_form = RegPais()
        return render(request, 'soccer/apuestas.html', {'league_form':league_form})


def match_all(request):
    today = datetime.now()
    date_from_match = today.strftime("%Y-%m-%d")
    lugar = '/home/jaime/partidos/' + date_from_match
    if not os.path.exists(lugar):
        os.mkdir(lugar)

    Nacion = request.POST['Nacion']
    league = request.POST['Liga']
    HomeTeam = request.POST['HomeTeam']
    AwayTeam = request.POST['AwayTeam']

    if Equipos.objects.filter(Nombre_Equipo=HomeTeam).count() != 1 or Equipos.objects.filter(
            Nombre_Equipo=AwayTeam).count() != 1:
        return redirect('futbol:form_general')

    probabilidadlocal, probabilidadvisita = promedio_goles(Nacion, league, HomeTeam, AwayTeam)
    if probabilidadlocal == 0:
        return redirect('futbol:form_general')

    evaluaciongoles = 8
    probloc, probvis = probabilidad_goles(probabilidadlocal, probabilidadvisita, evaluaciongoles)

    context = context_goles(evaluaciongoles, probloc, probvis)
    context['local_team'] = HomeTeam
    context['away_team'] = AwayTeam
    context['local'] = probloc
    context['visita'] = probvis
    template = get_template('forpdf.html')
    html = template.render(context)
    pdf = render_to_pdf('forpdf.html', context)

    if pdf:
        response = HttpResponse(pdf, content_type='application/pdf')
        filename = str(HomeTeam) + "vs" + str(AwayTeam) + ".pdf"
        content = "inline; filename="+filename
        content = "attachment; filename="+filename

        response['Content-Disposition'] = content

        return response

    return redirect('futbol:index')


def newmatch(request):
    actualizar_csv()
    context = {}
    with open('/home/jaime/PycharmProjects/Test1/Test/partidos_ayer.csv', 'r') as files:
        data = csv.reader(files)
        for row in data:

            nac = row[0].strip()
            league = row[1].strip()
            testeador = Ligas.objects.filter(Nacion=nac, Liga=league).count()

            if testeador == 0:
                for i in range(2):
                    if testeador == 1 or len(league.split("-")) == 1:
                        break
                    if len(league.split("-")) == 2:

                        leag, extra = league.split("-")
                    else:
                        leag, extra, extra1 = league.split("-")
                    leag = leag.strip()
                    league = leag
                    testeador = Ligas.objects.filter(Nacion=nac, Liga=league).count()

                if testeador == 0:
                    continue

            re = Ligas.objects.get(Nacion=nac, Liga=league)
            value = Partidos(Cod_Liga=re, HomeTeam=row[2], AwayTeam=row[3], date_match=row[4],
                             GoalsHome=int(row[5]), GoalsAway=int(row[6]), Result=row[7])
            try:
                value.save()
            except:
                context["error"] = "Fallo"

    context["exito"] = "Funciona"

    return render(request, 'soccer/add_ligas.html', context)

def add_ligas(request):
    context = {}
    a = 1
    with open('/home/jaime/PycharmProjects/Test1/Test/test1.csv', 'r') as files:
        data = csv.reader(files)
        for i in range(1):
            next(data)
        for row in data:
            value = Ligas(Nacion=row[0], Liga=row[1])
            try:
                value.save()
            except:
                context["error"] = "Fallo"
                a=0
                break
    if a:
        context["exito"] = "Funciona"
    return render(request,'soccer/add_ligas.html', context)


def add_matches(request):

    context = {}
    with open('/home/jaime/PycharmProjects/Test1/Test/partidos.csv', 'r') as files:
        data = csv.reader(files)
        for row in data:
            codigo_league = int(row[0])
            re = Ligas.objects.get(Codigo_liga=codigo_league)
            print (str(row))
            fecha = row[3]
            dia, mes, anho = fecha.split(".")
            dateoriginal = anho + "-" + mes + "-" + dia
            value = Partidos(Cod_Liga=re, HomeTeam=row[1], AwayTeam=row[2], date_match=dateoriginal, GoalsHome=int(row[4]), GoalsAway=int(row[5]), Result=row[6])
            try:
                value.save()
            except:
                context["error"] = "Fallo"

    context["exito"] = "Funciona"

    return render(request, 'soccer/add_ligas.html', context)


def actualizar_matches(request):

    with open('/home/jaime/PycharmProjects/Test1/Test/partidos_actualizador.csv', 'r') as files:
        data = csv.reader(files)
        for row in data:
            codigo_league = int(row[0])
            re = Ligas.objects.get(Codigo_liga=codigo_league)
            print(str(row))
            fecha = row[3]
            dia, mes, anho = fecha.split(".")
            dateoriginal = anho + "-" + mes + "-" + dia
            value = Partidos(Cod_Liga=re, HomeTeam=row[1], AwayTeam=row[2], date_match=dateoriginal,
                             GoalsHome=int(row[4]), GoalsAway=int(row[5]), Result=row[6])
            try:
                value.save()
            except:
                return redirect('futbol:error')

    return redirect('futbol:index')


def add_teams(request):

    context = {}
    with open('/home/jaime/PycharmProjects/Test1/Test/equipos.csv', 'r') as files:
        data = csv.reader(files)
        for row in data:
            value = Equipos(Nombre_Equipo=row[0])
            try:
                value.save()
            except:
                context["error"] = "Se repitio"

    context["exito"] = "Funciona"

    return render(request, 'soccer/add_ligas.html', context)

def general(request):

    if not os.path.exists('/home/jaime/PycharmProjects/Test1/Test/partidos_tomorrow.csv'):
        get_match_tomorrow()
    return redirect('futbol:form_general')


def formulario_general(request):
    league_form = Checking()
    return render(request, 'soccer/complete_form.html', {'league_form': league_form})

def download_pdfs(request):
    manipulate()
    return redirect('futbol:index')
