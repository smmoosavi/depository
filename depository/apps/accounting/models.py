from django.db import models


# Create your models here.

class Pilgrim(models.Model):
    first_name = models.CharField(max_length=254, null=True, blank=True)
    last_name = models.CharField(max_length=254)
    phone = models.CharField(max_length=50)
    country = models.CharField(max_length=50)
    city = models.CharField(max_length=100, null=True, blank=True)
    passport_id = models.CharField(max_length=20, null=True, blank=True)
    passport_pic = models.ImageField(null=True, blank=True)

    def __str__(self):
        return f'{first_name} {last_name} {country} {passport_id}'
