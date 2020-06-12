from django.db import models
from multiselectfield import MultiSelectField


class Unlocode(models.Model):
    UNKNOWN = '0'
    PORT = '1'
    RAIL = '2'
    ROAD = '3'
    AIRPORT = '4'
    POST = '5'
    MULTIMOD = '6'
    FIXTRANS = '7'
    BORDER = 'B'
    FUNCTION_CHOICES = [
        (UNKNOWN, 'Unknown'),
        (PORT, 'Port'),
        (RAIL, 'Rail'),
        (ROAD, 'Road'),
        (AIRPORT, 'Airport'),
        (POST, 'Post'),
        (MULTIMOD, 'Multimod'),
        (FIXTRANS, 'FixTrans'),
        (BORDER, 'Border'),
    ]
    ch = models.CharField(max_length=1)
    locode = models.CharField(max_length=6) # LOCODE = 'CC OOO' CC=country code, OOO=location code
    name = models.CharField(max_length=100)
    namewodiacritics = models.CharField(max_length=100)
    subdiv = models.CharField(max_length=3)
    functions = MultiSelectField(choices=FUNCTION_CHOICES)
    status = models.CharField(max_length=2)
    date = models.CharField(max_length=4)
    iata = models.CharField(max_length=3)
    coordinates = models.CharField(max_length=30)
    remarks = models.CharField(max_length=80)

    class Meta:
        ordering = ['locode']

    def __str__(self):
        return f"locode:'{self.locode}', name:'{self.namewodiacritics}', functions:'{self.functions}'"
