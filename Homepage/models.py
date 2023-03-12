from django.db import models

# Create your models here.

class FoodCategory(models.Model):
	categoryName = models.CharField(max_length=30)
	adminID = models.IntegerField()

	def __str__(self):
		return self.categoryName
