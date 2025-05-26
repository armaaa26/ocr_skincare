from django.db import models

class SkincareIngredient(models.Model):
    name = models.CharField(max_length=255)
    benefit = models.TextField()
    side_effect = models.TextField(blank=True, null=True)
    warning = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.name

