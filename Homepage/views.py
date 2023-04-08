import re
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404

from .models import FoodCategory, UserType, UserProfile, BusinessProfile, Rating
from .forms import FoodCategoryForm, UserRegistrationForm, BusinessRegistrationForm, RatingForm, UserUpdateForm, BusinessUpdateForm


import sys

location_options = [
        ('1', 'North'),
		('2', 'South'),
		('3', 'East'),
		('4', 'West'),
		('5', 'Central'),
    ]

gender_options = [
        ('M', 'Male'),
        ('F', 'Female'),
    ]

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

@login_required
def user_profile(request):
	context = {}
	foodCategory = FoodCategory.objects.all()
	if request.user.is_authenticated:
		user_type = UserType.objects.get(user=request.user)
		context = {'user_type':user_type}
		if user_type.userType == 'user':
			user_profile = UserProfile.objects.get(user=request.user)
			context = {'foodCategory':foodCategory, 'user_type':user_type, 'user_profile':user_profile, 'location_options': location_options, 'gender_options':gender_options}
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

@login_required
def food_category(request):
	user_type = UserType.objects.get(user=request.user)
	form = FoodCategoryForm()
	foodCategory = FoodCategory.objects.all()
	context = {'user_type': user_type, 'foodCategory':foodCategory,'form':form}
	return render(request, 'foodcategory.html', context)

@login_required
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

@login_required
def delete_food_category(request, food_category_id):
	item = FoodCategory.objects.get(pk=food_category_id)
	item.delete()
	messages.success(request,("Food Category Deleted!"))
	return redirect(food_category)

@login_required
def recommender_page(request):
	user_profile = None
	user_type = UserType.objects.get(user=request.user)
	foodCategory = FoodCategory.objects.all()
	has_rating = Rating.objects.filter(user=request.user).count() > 0

	if user_type.userType == 'user':
		user_profile = UserProfile.objects.get(user=request.user)

	context = {
		'user_type': user_type, 
		'foodCategory':foodCategory, 
		'user_profile':user_profile,
		'has_rating':has_rating,
		}
	return render(request, 'recommender.html', context)

def customer_support(request):
	context = {}
	if request.user.is_authenticated:
		user_type = UserType.objects.get(user=request.user)
		context = {'user_type': user_type}
	return render(request, 'customersupport.html', context)

@login_required
def admin_home(request):
	user_type = UserType.objects.get(user=request.user)
	context = {'user_type': user_type}
	return render(request, 'adminhome.html', context)

@login_required
def registered_businesses(request):
	user_type = UserType.objects.get(user=request.user)
	if user_type.userType in ['user','business']:
		businesses = BusinessProfile.objects.filter(user__is_active=True)
	else:
		businesses = BusinessProfile.objects.all()
	context = {'user_type': user_type, 'businesses':businesses}
	return render(request, 'registeredbusinesses.html', context)

@login_required
def user_home(request):
	user_type = UserType.objects.get(user=request.user)
	context = {'user_type': user_type}
	return render(request, 'userhome.html', context)

@login_required
def business_home(request):
	user_type = UserType.objects.get(user=request.user)
	context = {'user_type': user_type}
	return render(request, 'businesshome.html', context)

#not yet done
@login_required
def search_users(request):
	users = User.objects.all()
	user_type = UserType.objects.get(user=request.user)
	context = {'user_type': user_type, 'users':users}
	return render(request, 'searchusers.html', context)

@login_required
def user_promotion(request):
	users = User.objects.all()
	user_type = UserType.objects.get(user=request.user)
	context = {'user_type': user_type, 'users':users}
	return render(request, 'userpromotion.html', context)

@login_required
def recommender_results(request):
	recommended_food = "Curry chicken noodles"  # You may get this from your recommendation algorithm
	user_type = UserType.objects.get(user=request.user)
	form = RatingForm(request.POST)
	context = {
		'user_type': user_type,
		'recommended_food': recommended_food,
		'form': form,
		}
	return render(request, 'recommenderresults.html',context)

@login_required
def view_user_profile(request):
	user_type = UserType.objects.get(user=request.user)
	foodCategory = FoodCategory.objects.all()
	context = {
		'user_type': user_type, 
		'foodCategory':foodCategory, 
		'location_options':location_options, 
		'gender_options':gender_options
		}
	return render(request, 'viewuserprofile.html', context)

@login_required
def view_business_profile(request):
	user_type = UserType.objects.get(user=request.user)
	foodCategory = FoodCategory.objects.all()
	context = {'user_type': user_type, 'foodCategory':foodCategory, 'location_options':location_options}
	return render(request, 'viewbusinessprofile.html', context)

@login_required
def create_rating(request):
	recommended_food = "Curry chicken noodles"  # You may get this from your recommendation algorithm

	if request.method == 'POST':
		user = request.user
		food = request.POST.get('food', '')
		rating_value = request.POST.get('rating', None)

		context = {
			'recommended_food': recommended_food,
		}

		if rating_value is not None:
			rating_value = int(rating_value)
			if 1 <= rating_value <= 5:
				rating, created = Rating.objects.get_or_create(user=user, food=food, defaults={'rating': rating_value})
				# rating = Rating(user=user, food=food, rating=rating_value)
				rating.rating = rating_value
				rating.save()
				messages.success(request, ('Successfully rated! We will take this rating into account in your next reccomendation!'))
				return redirect(user_home)
		else:
			messages.error(request,('Please select a rating and try again!'))
	return render(request, 'recommenderresults.html', context)

@login_required
def food_quiz(request):
	foodQuizList = [
        ('Nasi Lemak'),
		('Fried Chicken'),
		('Chicken Rice'),
		('Chao Kway Tiao'),
		('Mixed Veg Rice'),
		('Mala'),
		('Nasi Biryani'),
		('Rojak'),
		('Mc Chicken'),
		('Dim Sum'),
    ]
	user_type = UserType.objects.get(user=request.user)
	has_rating = Rating.objects.filter(user=request.user).count() > 0

	context = {
		"foodQuizList": foodQuizList,
		"user_type": user_type,
	}
	if not has_rating:
		messages.warning(request, ('Please complete the Food Quiz before using the recommender for the first time!'))

	if request.method == 'POST':
		user = request.user
		for i in range(1,11):
			food = request.POST.get(f'food-{i}')
			rating_value = request.POST.get(f'rating-{i}')
			if rating_value is not None:
				rating_value = int(rating_value)
				if 1 <= rating_value <= 5:
					rating, created = Rating.objects.get_or_create(user=user, food=food, defaults={'rating': rating_value})
					rating.rating = rating_value
					rating.save()
		messages.success(request, ('Successfully rated! We will take these ratings into account in your next reccomendation!'))
		return render(request, 'foodquiz.html', context)
	
	return render(request, 'foodquiz.html', context)


@login_required
def update_user_profile(request):
	print("zx request: "+str(request),flush=True)
	if request.method == 'POST':
		form = UserUpdateForm(request.POST)
		print("zx form: "+str(form),flush=True)
		print("zx form.is_valid(): "+str(form.is_valid()),flush=True)
		print("Form errors: ", form.errors, flush=True)
		if form.is_valid():
			request.user.first_name = form.cleaned_data['first_name']
			request.user.last_name = form.cleaned_data['last_name']
			request.user.email = form.cleaned_data['email']
			request.user.username = form.cleaned_data['username']
			if form.cleaned_data['password']:
				request.user.set_password(form.cleaned_data['password'])
			request.user.save()

			if form.cleaned_data['password']:
				login(request, request.user)

			user_profile, created = UserProfile.objects.get_or_create(user=request.user)
			user_profile.age = form.cleaned_data['age']
			user_profile.phone = form.cleaned_data['phone']
			user_profile.favFood = form.cleaned_data['favorite_food']
			user_profile.prefLocation = form.cleaned_data['preferred_location']
			user_profile.foodCategory = form.cleaned_data['food_category']
			user_profile.gender = form.cleaned_data['gender']
			user_profile.save()

			messages.success(request, 'Your profile has been updated successfully.')
			return redirect('profile')
		else:
			messages.error(request, 'There was an error updating your profile. Please check your input.')
	else:
		form = UserRegistrationForm(initial={
			'first_name': request.user.first_name,
			'last_name': request.user.last_name,
			'age': request.user.userprofile.age,
			'email': request.user.email,
			'phone': request.user.userprofile.phone,
			'favorite_food': request.user.userprofile.favFood,
			'preferred_location': request.user.userprofile.prefLocation,
			'food_category': request.user.userprofile.foodCategory,
			'username': request.user.username,
			'gender': request.user.userprofile.gender,
		})

	context = {'form': form}
	return render(request, 'userprofile.html', context)

@login_required
def update_business_profile(request):
	if request.method == 'POST':
		form = BusinessUpdateForm(request.POST)
		print("zx form.is_valid(): "+str(form.is_valid()),flush=True)
		print("Form errors: ", form.errors, flush=True)
		if form.is_valid():
			request.user.first_name = form.cleaned_data['first_name']
			request.user.last_name = form.cleaned_data['last_name']
			request.user.email = form.cleaned_data['email']
			request.user.username = form.cleaned_data['username']
			if form.cleaned_data['password']:
				request.user.set_password(form.cleaned_data['password'])
			request.user.save()

			if form.cleaned_data['password']:
				login(request, request.user)

			business_profile, created = BusinessProfile.objects.get_or_create(user=request.user)
			business_profile.companyName = form.cleaned_data['company_name']
			business_profile.phone = form.cleaned_data['phone']
			business_profile.address = form.cleaned_data['address']
			business_profile.postalCode = form.cleaned_data['postal_code']
			business_profile.foodCategory = form.cleaned_data['food_category']
			business_profile.save()

			messages.success(request, 'Your business profile has been updated successfully.')
			return redirect('profile')
		else:
			messages.error(request, 'There was an error updating your business profile. Please check your input.')
	else:
		form = BusinessRegistrationForm(initial={
			'company_name': request.user.businessprofile.companyName,
			'uen': request.user.businessprofile.uen,
			'first_name': request.user.first_name,
			'last_name': request.user.last_name,
			'email': request.user.email,
			'phone': request.user.businessprofile.phone,
			'address': request.user.businessprofile.address,
			'postal_code': request.user.businessprofile.postalCode,
			'food_category': request.user.businessprofile.foodCategory,
			'username': request.user.username,
		})

	context = {'form': form}
	return render(request, 'userprofile.html', context)