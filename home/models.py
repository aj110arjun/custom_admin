from django.db import models


class UserAuths(models.Model):
    fullname = models.CharField(max_length=255)
    email = models.EmailField()
    password = models.CharField(max_length=255)

    def __str__(self):
        return self.fullname
