from django.db import models

class DatasetA(models.Model):
    id = models.AutoField(primary_key=True)
    nom = models.CharField(max_length=255)
    valeur = models.IntegerField()

    def __str__(self):
        return f"A-{self.nom} ({self.valeur})"


class DatasetB(models.Model):
    id = models.AutoField(primary_key=True)
    nom = models.CharField(max_length=255)
    valeur = models.IntegerField()

    def __str__(self):
        return f"B-{self.nom} ({self.valeur})"
    


class Ecart(models.Model):
    STATUS_CHOICES = [
        ('Identique', 'Identique'),
        ('Différent', 'Différent'),
        ('Nouveau', 'Nouveau'),
    ]

    METHODE_CHOICES = [
        ('Spark', 'Spark'),
        ('Django', 'Django'),
    ]

    nom = models.CharField(max_length=255)
    ecart_valeur = models.CharField(max_length=255)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES)
    methode = models.CharField(max_length=10, choices=METHODE_CHOICES)

    def __str__(self):
        return f"{self.nom} → {self.status} via {self.methode}"
