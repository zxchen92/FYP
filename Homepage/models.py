from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator


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
	locations = [
		('1', 'North'),
		('2', 'South'),
		('3', 'East'),
		('4', 'West'),
		('5', 'Central'),
	]
	GENDER_CHOICES = [
        ('M', 'Male'),
        ('F', 'Female'),
    ]
	user = models.OneToOneField(User, on_delete=models.CASCADE)
	age = models.IntegerField()
	phone = models.CharField(max_length=8)
	favFood = models.CharField(max_length=50)
	prefLocation = models.CharField(max_length=30, choices=locations)
	foodCategory = models.ForeignKey(FoodCategory, on_delete=models.CASCADE, related_name='user_food_category')
	gender = models.CharField(max_length=1, choices=GENDER_CHOICES, verbose_name='Gender')

	def __str__(self):
		return f"{self.user.username}'s profile: age {self.age}, phone {self.phone}, favorite food {self.favFood}, preferred location {self.prefLocation}, food category {self.foodCategory}, gender {self.gender}"

class BusinessProfile(models.Model):
	user = models.ForeignKey(User, on_delete=models.CASCADE)
	companyName = models.CharField(max_length=50)
	uen = models.CharField(max_length=10)
	phone = models.CharField(max_length=8)
	address = models.CharField(max_length=100)
	postalCode = models.CharField(max_length=6)
	foodCategory = models.ForeignKey(FoodCategory, on_delete=models.CASCADE, related_name='business_food_category')

	def __str__(self):
		return f"{self.companyName}'s profile: uen {self.uen}, phone {self.phone}, address {self.address}, postal code {self.postalCode}, food category {self.foodCategory}"

class Rating(models.Model):
	user = models.ForeignKey(User, on_delete=models.CASCADE)
	food = models.CharField(max_length=50)
	rating = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])

	def __str__(self):
		return f"{self.user.username} - {self.food} - {self.rating}"