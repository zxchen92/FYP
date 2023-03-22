from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib import messages
from django.shortcuts import get_object_or_404

from .models import FoodCategory, UserType, UserProfile, BusinessProfile
from .forms import FoodCategoryForm, UserRegistrationForm, BusinessRegistrationForm


import sys

def landing(request):
	context = {}
	if request.user.is_authenticated:
		user_type = UserType.objects.get(user=request.user)
		context = {'user_type': user_type}
	return render(request, 'landing.html', context)

def about(request):
	context = {}
	if request.user.is_authenticated:
		user_type = UserType.objects.get(user=request.user)
		context = {'user_type': user_type}
	return render(request, 'about.html', context)

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
				return redirect('businesshome')
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
	context = {}
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
		context = {'user_type':user_type}
		if user_type.userType == 'user':
			user_profile = UserProfile.objects.get(user=request.user)
			context = {'foodCategory':foodCategory, 'user_type':user_type, 'user_profile':user_profile, 'location_options': location_options}
		if user_type.userType == 'business':
			business_profile = BusinessProfile.objects.get(user=request.user)
			context = {'foodCategory':foodCategory, 'user_type':user_type, 'business_profile':business_profile}
	else:
		user_type=None
		user_profile=None
	return render(request, 'userprofile.html', context)

def register(request):
	return render(request, 'register.html', {})

def register_user(request):
	foodCategory = FoodCategory.objects.all()
	form = UserRegistrationForm(request.POST or None, request=request)
	if request.method == 'POST':
		if form.is_valid():
			user, user_profile, user_type = form.save(commit=False)
			user.save()
			user_profile.user = user
			user_profile.save()
			user_type.user = user
			user_type.save()
			if user is not None:
				login(request, user)
				messages.success(request, ('User registered!'))
				user_type = get_object_or_404(UserType, user=user)
				return redirect('userhome')
		else:
			messages.error(request,('User registration unsuccesful! Please try again!'))
			form = UserRegistrationForm()
	
	return render(request, 'registeruser.html', {'foodCategory':foodCategory,'form':form})

def register_business(request):
	foodCategory = FoodCategory.objects.all()
	form = BusinessRegistrationForm(request.POST or None, request=request)
	if request.method == 'POST':
		if form.is_valid():
			user, business_profile, user_type = form.save(commit=False)
			user.is_active = False
			user.save()
			business_profile.user = user
			business_profile.save()
			user_type.user = user
			user_type.save()
			if user is not None:
				messages.success(request, ('User registered! We will send a verifcation email to you when your business is verfied!'))
				return redirect('landing')
		else:
			messages.error(request,('User registration unsuccesful! Please try again!'))
			form = UserRegistrationForm()


	return render(request, 'registerbusiness.html', {'foodCategory':foodCategory,'form':form})

def food_category(request):
	user_type = UserType.objects.get(user=request.user)
	foodCategory = FoodCategory.objects.all()
	form = FoodCategoryForm()

	context = {'user_type': user_type, 'foodCategory':foodCategory,'form':form}
	return render(request, 'foodcategory.html', context)

def add_food_category(request):
	if request.method == 'POST':
		form = FoodCategoryForm(request.POST or None, request=request)
		print(form)
		sys.stdout.flush()
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
	user_profile = None
	user_type = UserType.objects.get(user=request.user)
	if user_type.userType == 'user':
		user_profile = UserProfile.objects.get(user=request.user)
	foodCategory = FoodCategory.objects.all()
	context = {'user_type': user_type, 'foodCategory':foodCategory, 'user_profile':user_profile}
	return render(request, 'recommender.html', context)

def customer_support(request):
	context = {}
	if request.user.is_authenticated:
		user_type = UserType.objects.get(user=request.user)
		context = {'user_type': user_type}
	return render(request, 'customersupport.html', context)

def admin_home(request):
	user_type = UserType.objects.get(user=request.user)
	context = {'user_type': user_type}
	return render(request, 'adminhome.html', context)

def registered_businesses(request):
	user_type = UserType.objects.get(user=request.user)
	if user_type.userType in ['user','business']:
		businesses = BusinessProfile.objects.filter(user__is_active=True)
	else:
		businesses = BusinessProfile.objects.all()
	context = {'user_type': user_type, 'businesses':businesses}
	return render(request, 'registeredbusinesses.html', context)

def user_home(request):
	user_type = UserType.objects.get(user=request.user)
	context = {'user_type': user_type}
	return render(request, 'userhome.html', context)

def business_home(request):
	user_type = UserType.objects.get(user=request.user)
	context = {'user_type': user_type}
	return render(request, 'businesshome.html', context)
#not yet done
def search_users(request):
	users = User.objects.all()
	user_type = UserType.objects.get(user=request.user)
	context = {'user_type': user_type, 'users':users}
	return render(request, 'searchusers.html', context)

def user_promotion(request):
	users = User.objects.all()
	user_type = UserType.objects.get(user=request.user)
	context = {'user_type': user_type, 'users':users}
	return render(request, 'userpromotion.html', context)