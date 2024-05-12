from django.db import models

# Create your models here.

class Matkul(models.Model):
    name = models.TextField(editable=True)

class Materi(models.Model):
    matkul = models.ForeignKey(Matkul, on_delete=models.CASCADE)
    name = models.TextField()

class Activity(models.Model):
    materi = models.ForeignKey(Materi, on_delete=models.CASCADE)
    id_num = models.TextField(null=True)
    type = models.TextField()
    name = models.TextField()
    url = models.URLField()
    deadline = models.DateTimeField(null=True)
    open_time = models.DateTimeField(null=True)

class NoticedOpenTimeActivity(models.Model):
    activity = models.ForeignKey(Activity, on_delete=models.CASCADE)
    noticed = models.BooleanField()

class NoticedDeadlineActivity(models.Model):
    activity = models.ForeignKey(Activity, on_delete=models.CASCADE)
    noticed = models.BooleanField()