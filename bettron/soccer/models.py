from django.db import models

# Create your models here.

from django.db import models

class Ligas(models.Model):

    Codigo_liga = models.AutoField(primary_key=True)
    Nacion = models.CharField(max_length=25)
    Liga = models.CharField(max_length=40)

    def __str__(self):
        return self.Nacion + "  " + self.Liga


class Equipos(models.Model):

    Nombre_Equipo = models.CharField(max_length=40,unique=True)

    def __str__(self):
        return self.Nombre_Equipo


class Partidos(models.Model):

    Cod_Liga = models.ForeignKey(Ligas, on_delete=models.PROTECT)
    HomeTeam = models.CharField(max_length=50)
    AwayTeam = models.CharField(max_length=50)
    date_match = models.DateField()
    GoalsHome = models.PositiveIntegerField()
    GoalsAway = models.PositiveIntegerField()
    Result = models.CharField(max_length=1)

    def __str__(self):
        return self.HomeTeam + " " + self.AwayTeam
