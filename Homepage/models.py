from django.db import models
from django.contrib.auth.models import User


# Create your models here.

class FoodCategory(models.Model):
	categoryName = models.CharField(max_length=30)
	adminID = models.IntegerField()

	def __str__(self):
		return self.categoryName

class UserType(models.Model):
	user = models.OneToOneField(User, on_delete=models.CASCADE)
	type_choices = [
		('admin', 'Admin'),
		('user', 'User'),
		('business', 'Business'),
	]
	userType = models.CharField(max_length=50, choices=type_choices)

	def __str__(self):
		return f"{self.user.username}'s type: {self.userType}"

class UserProfile(models.Model):
	userId = models.OneToOneField(User, on_delete=models.CASCADE)
	age = models.IntegerField()
	phone = models.CharField(max_length=8)
	favFood = models.CharField(max_length=30)
	prefLocation = models.CharField(max_length=30)
	foodCategory = models.ForeignKey(FoodCategory, on_delete=models.CASCADE, related_name='user_food_category')

	def __str__(self):
		return f"{self.user.username}'s profile: age {self.age}, phone {self.phone}, favorite food {self.favFood}, preferred location {self.prefLocation}, food category {self.foodCategory}"

class BusinessProfile(models.Model):
	userId = models.ForeignKey(User, on_delete=models.CASCADE)
	companyName = models.CharField(max_length=50)
	uen = models.CharField(max_length=10)
	phone = models.CharField(max_length=8)
	address = models.CharField(max_length=100)
	postalCode = models.CharField(max_length=6)
	foodCategory = models.ForeignKey(FoodCategory, on_delete=models.CASCADE, related_name='business_food_category')

	def __str__(self):
		return f"{self.companyName}'s profile: uen {self.uen}, phone {self.phone}, address {self.address}, postal code {self.postalCode}, food category {self.foodCategory}"
