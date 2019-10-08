from django.db import models

class equipo(models.Model):
    nombreteam = models.CharField(max_length=40,db_index=True)

    def __str__(self):
        return self.nombreteam

class competicion(models.Model):
    nombreliga = models.CharField(max_length=40,db_index=True)
    Anho = models.PositiveSmallIntegerField()

class participacion(models.Model):
    liga = models.ForeignKey(competicion,on_delete=models.PROTECT)
    equi = models.ForeignKey(equipo,on_delete=models.PROTECT)
    puntuacion = models.PositiveSmallIntegerField(default=0)

class Partido(models.Model):
    liga = models.ForeignKey(competicion,on_delete=models.PROTECT)
    host = models.ForeignKey(equipo,on_delete=models.PROTECT,related_name = 'home')
    away = models.ForeignKey(equipo,on_delete=models.PROTECT,related_name = 'away')
    Ganador = models.CharField(max_length=1)
    Fecha = models.DateField()

class DetallesPartidoGoles(models.Model):
    partido = models.ForeignKey(Partido,on_delete = models.PROTECT)
    GolesHalfHome = models.PositiveSmallIntegerField(default = 0)
    GolesHalfAway = models.PositiveSmallIntegerField(default = 0)
    ResultadoHalf = models.CharField(max_length=1)
    GolesFullHome = models.PositiveSmallIntegerField(default = 0)
    GolesFullAway = models.PositiveSmallIntegerField(default = 0)
