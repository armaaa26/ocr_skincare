from django.db import models

class SkincareIngredient(models.Model):
    name = models.CharField(max_length=255, unique=True)
    benefit = models.TextField()

    def __str__(self):
        return self.name
