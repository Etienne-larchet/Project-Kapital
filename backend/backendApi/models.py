from django.db import models

class GeneralModel(models.Model):
    timeout = models.IntegerField()
    
    class Meta:
        abstract = True

class SecSearch(GeneralModel):
    ticker = models.CharField(max_length=8)
    fromDate = models.DateField()
    toDate = models.DateField()
    formType = models.IntegerField(choices=[(0,'4'), (1,'8k'), (2,'10k'), (3,'10q'), (4,'11k'), (5,'ars')])