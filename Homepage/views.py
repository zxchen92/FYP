from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib import messages
from django.shortcuts import get_object_or_404

from .models import FoodCategory, UserType, UserProfile, BusinessProfile
from .forms import FoodCategoryForm, UserRegistrationForm


import sys


def landing(request):
	return render(request, 'landing.html', {})

def about(request):
	return render(request, 'about.html', {})

def login_user(request):
	if request.method == 'POST':
		username = request.POST['username']
		password = request.POST['password']
		user = authenticate(request, username=username, password=password)
		print('zx')
		print(user)
		sys.stdout.flush()
		if user is not None:
			login(request, user)
			messages.success(request,('Login succesful!'))
			user_type = get_object_or_404(UserType, user=user)
			if user_type.userType == 'admin':
				return redirect('adminhome')
			elif user_type.userType == 'user':
				return redirect('userhome')
			else:
				return redirect('landing')
		else:
			messages.error(request,('Login unsuccesful! Please try again!'))
			return redirect('login')
	else:

		return render(request, 'login.html', {})

def logout_user(request):
	logout(request)
	messages.success(request, ('Logout succesful!'))
	return redirect('landing')

def user_profile(request):
	foodCategory = FoodCategory.objects.all()
	location_options = [
        ('1', 'North'),
		('2', 'South'),
		('3', 'East'),
		('4', 'West'),
		('5', 'Central'),
    ]
	if request.user.is_authenticated:
		user_type = UserType.objects.get(user=request.user)
		user_profile = UserProfile.objects.get(user=request.user)
	else:
		user_type=None
		user_profile=None
	return render(request, 'userprofile.html', {'foodCategory':foodCategory, 'user_type':user_type, 'user_profile':user_profile, 'location_options': location_options})

def register(request):
	return render(request, 'register.html', {})

def register_user(request):
	foodCategory = FoodCategory.objects.all()
	form = UserRegistrationForm(request.POST or None, request=request)
	if request.method == 'POST':
		print('zx:')
		print(form)
		sys.stdout.flush()
		if form.is_valid():
			user, user_profile, user_type = form.save(commit=False)
			user.save()
			user_profile.userId = user
			user_profile.save()
			user_type.user = user
			user_type.save()
			if user is not None:
				login(request, user)
				messages.success(request, ('User registered!'))
				user_type = get_object_or_404(UserType, user=user)
				if user_type.userType == 'admin':
					return redirect('adminhome')
				elif user_type.userType == 'user':
					return redirect('userhome')
				else:
					return redirect('landing')
		else:
			messages.error(request,('User registration unsuccesful! Please try again!'))
			form = UserRegistrationForm()
	
	return render(request, 'registeruser.html', {'foodCategory':foodCategory,'form':form})

def register_business(request):
	foodCategory = FoodCategory.objects.all()
	return render(request, 'registerbusiness.html', {'foodCategory':foodCategory})

def food_category(request):

	foodCategory = FoodCategory.objects.all()
	form = FoodCategoryForm()

	return render(request, 'foodcategory.html', {'foodCategory':foodCategory,'form':form})

def add_food_category(request):
	if request.method == 'POST':
		form = FoodCategoryForm(request.POST or None, request=request)

		if form.is_valid():
			form.save()
			messages.success(request, ("Food Category has been added!"))
			return redirect(food_category)
		else:
			form = FoodCategoryForm()

	return redirect(food_category)

def delete_food_category(request, food_category_id):
	item = FoodCategory.objects.get(pk=food_category_id)
	item.delete()
	messages.success(request,("Food Category Deleted!"))
	return redirect(food_category)

def recommender_page(request):
	return render(request, 'recommender.html', {})

def customer_support(request):
	return render(request, 'customersupport.html', {})

def admin_home(request):
	return render(request, 'adminhome.html', {})

def registered_businesses(request):
	return render(request, 'registeredbusinesses.html', {})

def user_home(request):
	return render(request, 'userhome.html', {})
