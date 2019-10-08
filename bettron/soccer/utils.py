from io import BytesIO
from django.http import HttpResponse
from django.template.loader import get_template
from .models import *
from django.db.models import Avg, Count
import math
from xhtml2pdf import pisa
import os
from selenium import webdriver
import csv
import time
import shutil
from PyPDF2 import PdfFileMerger
from datetime import datetime, timedelta


def actualizar_csv():
    browser = webdriver.Chrome('/home/jaime/PycharmProjects/Test1/chromedriver')

    url = 'https://www.scoreboard.com/en/soccer/'

    browser.get(url)
    time.sleep(5)

    el = browser.find_elements_by_xpath("/html/body/div[2]/div[3]/div[2]/div[1]/div[5]/div[3]/ul/li[4]/span[1]")
    cantidaddias = 1
    for i in range(cantidaddias):
        el[0].click()
        time.sleep(5)
        el = browser.find_elements_by_xpath("/html/body/div[2]/div[3]/div[2]/div[1]/div[5]/div[3]/ul/li[4]/span[1]")

    tablas = browser.find_elements_by_xpath("//table[@class = 'soccer']")
    cantidad_tablas = len(tablas)
    today = datetime.now()
    daysless = timedelta(days=cantidaddias)
    date_from_match = today - daysless
    date_from_match = date_from_match.strftime("%Y-%m-%d")

    with open('/home/jaime/PycharmProjects/Test1/Test/partidos_ayer.csv', 'w') as file:
        for i in range(cantidad_tablas):

            tabla_lei = (tablas[i].text).split("\n")
            lines_tabla = len(tabla_lei)
            j = 0
            if len(tabla_lei[0].split(":")) == 2:
                Lugar, Liga = tabla_lei[0].split(":")
                j = 1
            else:
                Lugar, Liga = tabla_lei[1].split(":")
                j = 2

            Lugar = Lugar.lower()
            Lugar = Lugar[0].upper() + Lugar[1:]

            print(Lugar + " " + Liga + "\n\n")

            while j < lines_tabla:
                helper = tabla_lei[j]
                helper = helper.strip()

                if lines_tabla - j < 4:
                    break

                #
                if len(helper.split("-")) == 2:
                    j += 1
                    continue

                elif len(helper.split(" ")) == 2:
                    hour, checking = helper.split(" ")

                else:
                    hour, checking, extra = helper.split(" ")

                if checking == "Postponed" or checking == "Cancelled" or checking == 'FRO' or checking == "Awarded":
                    j += 4
                    continue

                home_team = tabla_lei[j + 1]
                if len(tabla_lei[j + 3].split("-")) == 2 and tabla_lei[j + 3][0] == '(':
                    goals_home, goals_away = tabla_lei[j + 3].split("-")
                    goals_home = goals_home.replace('(', ' ')
                    goals_away = goals_away.replace(')', ' ')
                    away_team = tabla_lei[j + 4]
                    j += 5
                else:
                    goals_home, goals_away = tabla_lei[j + 2].split("-")
                    away_team = tabla_lei[j + 3]
                    j += 4

                finalresult = 'H'
                if int(goals_home) == int(goals_away):
                    finalresult = 'D'
                elif int(goals_home) < int(goals_away):
                    finalresult = 'A'

                res = Lugar + "," + Liga + "," + home_team + "," + away_team + "," + date_from_match + "," + goals_home + "," + goals_away + "," + finalresult + "\n"
                print(res)
                file.write(res)

    browser.quit()

def poisson(media,number):

    var1 = (math.e)**(-media)
    var2 = media ** number
    var3 = math.factorial(number)
    poisson = var1*var2/var3

    return poisson


def promedio_goles(Nacion, league, HomeTeam, AwayTeam):

    Instanciador = Ligas.objects.get(Nacion=Nacion, Liga=league)
    promediogolestemporada = Partidos.objects.filter(Cod_Liga=Instanciador).aggregate(GoalsHome=Avg('GoalsHome'), GoalsAway=Avg('GoalsAway'))

    promediogoleslocal = Partidos.objects.filter(Cod_Liga=Instanciador, HomeTeam=HomeTeam).aggregate(GoalsHome=Avg('GoalsHome'), GoalsAway=Avg('GoalsAway'))
    promediogolesvisita = Partidos.objects.filter(Cod_Liga=Instanciador, AwayTeam=AwayTeam).aggregate(GoalsHome=Avg('GoalsHome'), GoalsAway=Avg('GoalsAway'))

    if promediogoleslocal['GoalsHome'] is None or promediogoleslocal['GoalsAway'] is None:
        return 0, 0
    if promediogolesvisita['GoalsHome'] is None or promediogolesvisita['GoalsAway'] is None:
        return 0, 0

    ataquelocal = promediogoleslocal['GoalsHome'] / promediogolestemporada['GoalsHome']
    defensalocal = promediogoleslocal['GoalsAway'] / promediogolestemporada['GoalsHome']

    ataquevisita = promediogolesvisita['GoalsAway'] / promediogolestemporada['GoalsAway']
    defensavisita = promediogolesvisita['GoalsHome'] / promediogolestemporada['GoalsAway']

    probabilidadlocal = ataquelocal * defensavisita * promediogolestemporada['GoalsHome']
    probabilidadvisita = ataquevisita * defensalocal * promediogolestemporada['GoalsAway']

    return probabilidadlocal, probabilidadvisita


def probabilidad_goles(probabilidadlocal,probabilidadvisita,evaluaciongoles):
    probloc = []
    probvis = []
    for i in range(evaluaciongoles):
        probloc.append(round(poisson(probabilidadlocal, i) * 100, 3))
        probvis.append(round(poisson(probabilidadvisita, i) * 100, 3))

    return probloc, probvis


def context_goles(evaluaciongoles, probloc, probvis):
    context = {}
    goles = []
    matrixresult = [0] * evaluaciongoles
    for i in range(evaluaciongoles):
        matrixresult[i] = [0] * evaluaciongoles
        goles.append(i)

    probablidadempate = 0
    probabilidadganarlocal = 0
    probabilidadganarvisitante = 0

    for i in range(evaluaciongoles):
        for j in range(evaluaciongoles):
            matrixresult[i][j] = round(probloc[j] * probvis[i] / 100, 3)
            if i == j:
                probablidadempate += matrixresult[i][j]
            elif j > i:
                probabilidadganarlocal += matrixresult[i][j]
            else:
                probabilidadganarvisitante += matrixresult[i][j]

    noambosanotan = matrixresult[0][0]
    for i in range(1, evaluaciongoles):
        noambosanotan += matrixresult[0][i] + matrixresult[i][0]

    ambosanotan = round(100 - noambosanotan, 3)
    noambosanotan = round(noambosanotan, 3)

    # goles mayores a:
    cantidadgolesmaxima = evaluaciongoles * 2 - 1
    probcantgoles = [0] * cantidadgolesmaxima

    for i in range(evaluaciongoles):
        for j in range(evaluaciongoles):
            probcantgoles[i + j] += matrixresult[i][j]

    for i in range(cantidadgolesmaxima):
        probcantgoles[i] = round(probcantgoles[i], 3)

    for i in range(1, cantidadgolesmaxima):
        probcantgoles[i] += probcantgoles[i - 1]
        probcantgoles[i] = round(probcantgoles[i], 3)

    # Bucles para evaluar mas y menos goles en la pagina html
    goles1 = []
    for i in range(5):
        goles1.append(i)

    goles2 = []
    for i in range(1, 6):
        goles2.append(i)

    # goles menores a:
    probcantgolesmay = [0] * cantidadgolesmaxima
    for i in range(cantidadgolesmaxima):
        probcantgolesmay[i] = round(100 - probcantgoles[i], 3)

    for i in range(5, cantidadgolesmaxima):
        probcantgoles.pop()
        probcantgolesmay.pop()

    context['masgoles'] = probcantgolesmay
    context['menosgoles'] = probcantgoles
    context['matrix0'] = matrixresult[0]
    context['matrix1'] = matrixresult[1]
    context['matrix2'] = matrixresult[2]
    context['matrix3'] = matrixresult[3]
    context['matrix4'] = matrixresult[4]
    context['matrix5'] = matrixresult[5]
    context['matrix6'] = matrixresult[6]
    context['matrix7'] = matrixresult[7]
    context['goles'] = goles
    context['goles1'] = goles1
    context['goles2'] = goles2

    context['localvictoria'] = probabilidadganarlocal
    context['empate'] = probablidadempate
    context['visitantevictoria'] = probabilidadganarvisitante

    context['aa'] = ambosanotan
    context['naa'] = noambosanotan

    return context

def render_to_pdf(template_src, context_dict={}):
    template = get_template(template_src)
    html = template.render(context_dict)
    result = BytesIO()
    pdf = pisa.pisaDocument(BytesIO(html.encode("ISO-8859-1")), result)
    if not pdf.err:
        return HttpResponse(result.getvalue(), content_type='application/force-download')
    return None


def estaliga(nacion, liga):


    value = Ligas.objects.filter(Nacion=nacion, Liga=liga).count()
    print(str(value) + "\n" + nacion + "\t" + liga)
    value = int(value)

    if value:
        return True
    else:
        return False

def get_match_tomorrow():
    browser = webdriver.Chrome('/home/jaime/PycharmProjects/Test1/chromedriver')

    url = 'https://www.scoreboard.com/en/soccer/'

    browser.get(url)
    time.sleep(12)
    #el = browser.find_elements_by_xpath("/html/body/div[2]/div[3]/div[2]/div[1]/div[5]/div[3]/ul/li[4]/span[3]/span/span")
    #el[0].click()
    #time.sleep(5)
    tablas = browser.find_elements_by_xpath("//table[@class = 'soccer']")
    time.sleep(3)
    cantidad_tablas = len(tablas)
    print(str(cantidad_tablas))
    with open('/home/jaime/PycharmProjects/Test1/Test/partidos_tomorrow.csv', 'w') as file:
        for i in range(cantidad_tablas):
            tabla_lei = (tablas[i].text).split("\n")
            lines_tabla = len(tabla_lei)
            j = 0
            if len(tabla_lei[0].split(":")) == 2:
                Lugar, Liga = tabla_lei[0].split(":")
                j = 1
            else:
                Lugar, Liga = tabla_lei[1].split(":")
                j = 2
            Lugar = Lugar.strip()
            Liga = Liga.strip()
            Lugar = Lugar.lower()
            Lugar = Lugar[0].upper() + Lugar[1:]
            fail = False
            while True:
                if estaliga(Lugar, Liga):
                    break
                if len(Liga.split("-")) == 2:
                    Liga, Special = Liga.split("-")
                else:
                    extra = Liga.split("-")
                    Liga = extra[0]
                    fail = True
                    break
            if fail:
                continue
            print(Lugar + " " + Liga)
            while j < lines_tabla:
                if lines_tabla - j < 4:
                    break
                if tabla_lei[j + 1] == "FRO":
                    j += 1
                elif tabla_lei[j + 1] == "Postponed" or tabla_lei[j + 1] == "Finished" or tabla_lei[j + 1].isdigit():
                    j += 4
                    continue

                home_team = tabla_lei[j + 1]
                if tabla_lei[j + 2] == '-':
                    away_team = tabla_lei[j + 3]
                    j += 4
                else:
                    away_team = tabla_lei[j + 2]
                    j += 3
                variable = Lugar + "," + Liga + "," + home_team + "," + away_team
                print(variable)
                file.write(variable + "\n")
    browser.quit()

def manipulate():
    browser = webdriver.Chrome('/home/jaime/PycharmProjects/Test1/chromedriver')
    today = datetime.now()
    date_from_match = today.strftime("%Y-%m-%d")
    url = 'http://127.0.0.1:8000/soccer/'
    dir_download = '/home/jaime/Downloads/'
    dest_directory = '/home/jaime/partidos/' + date_from_match
    browser.get(url)
    time.sleep(2)
    el = browser.find_elements_by_xpath("//a[@id = 'tomorrow']")
    el[0].click()
    time.sleep(3)
    with open('/home/jaime/PycharmProjects/Test1/Test/partidos_tomorrow.csv', 'r') as file:
        data = csv.reader(file)
        for row in data:

            nacion, liga, local, visitante = row
            Nacion = browser.find_element_by_xpath("//input[@name = 'Nacion']")
            Nacion.clear()
            Nacion.send_keys(nacion)

            League = browser.find_element_by_xpath("//input[@name = 'Liga']")
            League.clear()
            League.send_keys(liga)

            HomeTeam = browser.find_element_by_xpath("//input[@name = 'HomeTeam']")
            HomeTeam.clear()
            HomeTeam.send_keys(local)

            AwayTeam = browser.find_element_by_xpath("//input[@name = 'AwayTeam']")
            AwayTeam.clear()
            AwayTeam.send_keys(visitante)

            Pred = browser.find_elements_by_xpath("//input[@id = 'Sending']")
            Pred[0].click()
            time.sleep(3)
            namefile = str(local) + "vs" + str(visitante) + ".pdf"
            namefile = dir_download+namefile
            if not os.path.exists(namefile):
                continue
            shutil.move(namefile, dest_directory)

    mergepdf(dest_directory)
    browser.quit()


def mergepdf(src):
    pdfs = []
    files = os.listdir(src)

    for file in files:
        (name, extend) = os.path.splitext(file)
        if extend == ".pdf":
            pdfs.append(src + "/" + file)

    merger = PdfFileMerger()

    for pdf in pdfs:
        merger.append(open(pdf, 'rb'))

    dest = src + "/" + "result.pdf"
    merger.write(dest)

    for file in pdfs:
        os.remove(file)

    os.remove('/home/jaime/PycharmProjects/Test1/Test/partidos_tomorrow.csv')
    merger.close()



