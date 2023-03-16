import re
from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm

from .models import FoodCategory, UserType, UserProfile, BusinessProfile

class FoodCategoryForm(forms.ModelForm):
	categoryName = forms.CharField(max_length=30)

	def __init__(self, *args, **kwargs):
		self.request = kwargs.pop('request', None)
		super(FoodCategoryForm, self).__init__(*args, **kwargs)

	def save(self, commit=True, *args, **kwargs):
		instance = super(FoodCategoryForm, self).save(commit=False, *args, **kwargs)
		instance.categoryName = self.cleaned_data['categoryName']
		instance.adminID = self.request.user.id
		if commit:
			instance.save()
		return instance

	class Meta:
		model = FoodCategory
		fields = ["categoryName"]

class UserRegistrationForm(forms.Form):
	location_choices = [
		(' ', '---------'),
		('north', 'North'),
		('south', 'South'),
		('east', 'East'),
		('west', 'West'),
		('central', 'Central'),
	]
	first_name = forms.CharField(max_length=30)
	last_name = forms.CharField(max_length=30)
	age = forms.IntegerField()
	email = forms.EmailField()
	phone = forms.CharField(max_length=8)
	favorite_food = forms.CharField(max_length=30)
	preferred_location = forms.ChoiceField(choices=location_choices)
	food_category = forms.ModelChoiceField(queryset=FoodCategory.objects.all())
	username = forms.CharField(max_length=30)
	password = forms.CharField(widget=forms.PasswordInput)

	def __init__(self, *args, **kwargs):
		self.request = kwargs.pop('request', None)
		super(UserRegistrationForm, self).__init__(*args, **kwargs)

	def clean_preferred_location(self):
		preferred_location = self.cleaned_data.get('preferred_location')
		if not preferred_location:
			raise forms.ValidationError("Please select a valid location.")
		return preferred_location

	def clean_phone(self):
		phone = self.cleaned_data.get('phone')
		if not re.match(r'^\d{8}$', phone):
			raise forms.ValidationError("Please enter a valid phone number")
		return phone

	# Override the default save method to save to UserProfile and UserType models
	def save(self):
		user = User.objects.create_user(
			username=self.cleaned_data['username'],
			password=self.cleaned_data['password'],
			email=self.cleaned_data['email'],
			first_name=self.cleaned_data['first_name'],
			last_name=self.cleaned_data['last_name']
		)

		user_profile = UserProfile.objects.create(
			userId=user,
			age=self.cleaned_data['age'],
			phone=self.cleaned_data['phone'],
			favFood=self.cleaned_data['favorite_food'],
			prefLocation=self.cleaned_data['preferred_location'],
			foodCategory=self.cleaned_data['food_category']
		)

		user_type = UserType.objects.create(
			user=user,
			type='user'
		)

		return (user, user_profile, user_type)