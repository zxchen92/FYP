from pickle import TRUE
import re
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404
from django.utils import timezone
import numpy as np
import pandas as pd
import tensorflow as tf
import sklearn
from sklearn.preprocessing import MinMaxScaler


from .food_recommender import get_recommendations
from .models import FoodCategory,UserProfile,UserType,BusinessProfile,Rating,Food,Promotion
from .forms import UserRegistrationForm,BusinessRegistrationForm,FoodCategoryForm,RatingForm,UserUpdateForm,BusinessUpdateForm,PromotionForm


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
	businesses = BusinessProfile.objects.filter(isVerified=False)
	not_verified_count = businesses.count()
	context = {
		'user_type': user_type,
		'businesses':businesses,
		'not_verified_count':not_verified_count
		}
	return render(request, 'adminhome.html', context)

@login_required
def search_businesses(request):
	user_type = UserType.objects.get(user=request.user)
	if user_type.userType in ['user','business']:
		businesses = BusinessProfile.objects.filter(user__is_active=True)
	else:
		businesses = BusinessProfile.objects.all()
	context = {'user_type': user_type, 'businesses':businesses}
	return render(request, 'searchbusinesses.html', context)

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
	# Get all UserType instances with userType equal to 'user'
	user_types = UserType.objects.filter(userType__in=['user'])
	# Get the related User instances
	users = [user_type.user for user_type in user_types]

	user_type = UserType.objects.get(user=request.user)
	context = {'user_type': user_type, 'users':users}
	return render(request, 'searchusers.html', context)

@login_required
def view_promotion(request, promotion_id=None):
	users = User.objects.all()
	user_type = UserType.objects.get(user=request.user)
	promotion = Promotion.objects.get(id=promotion_id)
	context = {
		'user_type': user_type,
		'users':users,
		'promotion':promotion,
		}
	return render(request, 'viewpromotion.html', context)

# @login_required
# def recommender_results(request):
# 	user_id = request.user.id
# 	rand= 0
# 	recommendations, recommendationsTwo = get_recommendations(user_id)
# 	food_id = recommendations[0]  # get the first food id from the recommendations list
# 	food = get_object_or_404(Food, id=food_id)  # query the database for the food object with the given id
# 	food_name = food.foodName  # get the name of the food
# 	maps_url = f"https://www.google.com/maps/search/?api=1&query={food_name.replace(' ', '+')}"
# 	maps_link = f'<a href="{maps_url}" target="_blank">{food_name}!!</a>'


# 	food_dict={}
# 	for foodid in recommendationsTwo:
# 		try:
# 			food2 =  get_object_or_404(Food, id=foodid)#Food.objects.get(Food, id=foodid)
# 			food_dict[foodid] = food2
# 			# food_name = food.foodName  # get the name of the food
# 			# maps_url = f"https://www.google.com/maps/search/?api=1&query={food_name.replace(' ', '+')}"
# 			# maps_link = f'<a href="{maps_url}" target="_blank">{food_name.foodName}</a>'

# 		except Food.DoesNotExist:
# 			pass

# 	####### Below is the prototype code ########
# 	user_type = UserType.objects.get(user=request.user)
# 	form = RatingForm(request.POST)
# 	############################################
# 	context = {
# 	'user_type': user_type,
# 	'form': form,
# 	#'full_recommendations' : full_recommendations,
# 	#'recommendations': recommendations,
# 	#'recommendationsTwo' : recommendationsTwo,
# 	'food_name' : food_name,
# 	'maps_link' : maps_link,
# 	#'food_dict' : food_dict,
# 	}

# 	ratings = Rating.objects.filter(user=request.user).values('food')
# 	rating_count = ratings.distinct().count()


# 	if rating_count > 30 :
# 		context['recommendations'] = recommendations

# 	else:
# 		context['recommendations'] = food_dict


# 	return render(request, 'recommenderresults.html',context)

@login_required
def recommender_results(request):
	user_id = request.user.id
	rand= 0
	recommendations, recommendationsTwo = get_recommendations(user_id)





	####### Below is the prototype code ########
	user_type = UserType.objects.get(user=request.user)
	form = RatingForm(request.POST)
	############################################
	context = {
	'user_type': user_type,
	'form': form,
	#'full_recommendations' : full_recommendations,
	#'recommendations': recommendations,
	#'recommendationsTwo' : recommendationsTwo,
	#'food_name' : food_name,
	#'maps_link' : maps_link,
	#'food_dict' : food_dict,
	}

	ratings = Rating.objects.filter(user=request.user).values('food')
	rating_count = ratings.distinct().count()


	if rating_count > 1 :
		food_dict = {}
		food_id = recommendations[0]  # get the first food id from the recommendations list
		food = get_object_or_404(Food, id=food_id)  # query the database for the food object with the given id
		food_dict[0] = food
		# food_name = food.foodName  # get the name of the food
		# maps_url = f"https://www.google.com/maps/search/?api=1&query={food_name.replace(' ', '+')}"
		# maps_link = f'<a href="{maps_url}" target="_blank">{food_name}!!</a>'
		#food_dict={}
		# for foodid in recommendations:
		# 	try:
		# 		food2 =  get_object_or_404(Food, id=foodid)
		# 		food_dict[foodid] = food2
				
		# 	except Food.DoesNotExist:
		# 		pass

		context['recommendations'] = food_dict
		#context['maps_link'] = maps_link

	else:
		food_dict={}
		for foodid in recommendationsTwo:
			try:
				food2 =  get_object_or_404(Food, id=foodid)
				food_dict[foodid] = food2

			except Food.DoesNotExist:
				pass
		context['recommendations'] = food_dict


	return render(request, 'recommenderresults.html',context)

@login_required
def recommender_normal(request):
	user_id = request.user.id
	recommendations, recommendationsTwo = get_recommendations(user_id)

	food_recommendations = get_recommendations(user_id)
	food_dict = {}
	for foodid in food_recommendations:
		try:
			food =  Food.objects.get(id=foodid)
			food_dict[foodid] = food
			# food_name = food.foodName  # get the name of the food
			# maps_url = f"https://www.google.com/maps/search/?api=1&query={food_name.replace(' ', '+')}"
			# maps_link = f'<a href="{maps_url}" target="_blank">{food_name.foodName}</a>'

		except Food.DoesNotExist:
			pass

	context = {
		'food_dict' : food_dict,
	}

	return render(request,'nomlrecommender.html', context)

# @login_required #RecommenderML integration test
# def recommender_ML(request):
# 	user_id = request.user.id
# 	recommendations = get_recommendations(user_id)
# 	food_id = recommendations[0]  # get the first food id from the recommendations list
# 	food = get_object_or_404(Food, id=food_id)  # query the database for the food object with the given id
# 	food_name = food.foodName  # get the name of the food
# 	context = {
# 		'recommendations': recommendations,
# 		'food_name' : food_name
# 		}

#	return render(request, 'recommenderml.html', context)

@login_required
def view_user_profile(request, user_id):
	selected_user = User.objects.get(id=user_id)
	selected_user_profile  = UserProfile.objects.get(user=selected_user)
	user_type = UserType.objects.get(user=request.user)
	foodCategory = FoodCategory.objects.all()
	disabled = ''
	if user_type.userType != "admin":
		disabled = "disabled"
	context = {
		'user_type': user_type,
		'foodCategory':foodCategory,
		'location_options':location_options,
		'gender_options':gender_options,
		'selected_user': selected_user,
		'selected_user_profile': selected_user_profile,
		'disabled':disabled,
		}
	return render(request, 'viewuserprofile.html', context)

@login_required
def view_business_profile(request, user_id):
	selected_business = User.objects.get(id=user_id)
	selected_business_profile  = BusinessProfile.objects.get(user=selected_business)
	user_type = UserType.objects.get(user=request.user)
	foodCategory = FoodCategory.objects.all()
	disabled = ''
	if user_type.userType != "admin":
		disabled = "disabled"
	context = {
		'user_type': user_type,
		'foodCategory':foodCategory,
		'location_options':location_options,
		'selected_business':selected_business,
		'selected_business_profile':selected_business_profile,
		'disabled':disabled,
		}
	return render(request, 'viewbusinessprofile.html', context)

@login_required
def create_rating(request):
	# recommended_food = "Curry chicken noodles"  # You may get this from your recommendation algorithm

	if request.method == 'POST':
		user = request.user
		food = request.POST.get('food', '')
		rating_value = request.POST.get('rating', None)

		if rating_value is not None:
			rating_value = int(rating_value)
			if 1 <= rating_value <= 5:
				rating, created = Rating.objects.get_or_create(user=user, food=food, defaults={'rating': rating_value})
				rating.rating = rating_value
				print("zx rating: "+str(rating),flush=True)
				rating.save()
				messages.success(request, ('Successfully rated! We will take this rating into account in your next reccomendation!'))
				return redirect(user_home)
		else:
			messages.error(request,('Please select a rating and try again!'))
	return redirect(request, 'recommenderresults.html')

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
def update_user_profile(request, user_id=None):
	# Check if the user is an admin and a user_id is provided
	is_admin_editing = user_id is not None and UserType.objects.get(user=request.user).userType == 'admin'

	# If admin is editing, get the user instance to be edited; otherwise, use the request.user instance
	user_to_edit = User.objects.get(id=user_id) if is_admin_editing else request.user

	if request.method == 'POST':
		form = UserUpdateForm(request.POST)
		print("Form errors: ", form.errors, flush=True)
		if form.is_valid():
			user_to_edit.first_name = form.cleaned_data['first_name']
			user_to_edit.last_name = form.cleaned_data['last_name']
			user_to_edit.email = form.cleaned_data['email']
			user_to_edit.username = form.cleaned_data['username']
			if form.cleaned_data['password']:
				user_to_edit.set_password(form.cleaned_data['password'])
			user_to_edit.save()

			# If admin is editing, update the is_active status
			if is_admin_editing:
				is_active = request.POST.get('is_active') != 'on'
				user_to_edit.is_active = is_active
				user_to_edit.save()

			else:
				if form.cleaned_data['password']:
					login(request, user_to_edit)

			user_profile, created = UserProfile.objects.get_or_create(user=user_to_edit)
			user_profile.age = form.cleaned_data['age']
			user_profile.phone = form.cleaned_data['phone']
			user_profile.favFood = form.cleaned_data['favorite_food']
			user_profile.prefLocation = form.cleaned_data['preferred_location']
			user_profile.foodCategory = form.cleaned_data['food_category']
			user_profile.gender = form.cleaned_data['gender']
			user_profile.save()

			messages.success(request, 'Profile has been updated successfully.')
			if is_admin_editing and user_id:
				return redirect('viewuserprofile', user_id=user_id)
			else:
				return redirect('profile')
		else:
			messages.error(request, 'There was an error in updating the profile. Please check your input(s).')
	else:
		form = UserRegistrationForm(initial={
			'first_name': user_to_edit.first_name,
			'last_name': user_to_edit.last_name,
			'age': user_to_edit.userprofile.age,
			'email': user_to_edit.email,
			'phone': user_to_edit.userprofile.phone,
			'favorite_food': user_to_edit.userprofile.favFood,
			'preferred_location': user_to_edit.userprofile.prefLocation,
			'food_category': user_to_edit.userprofile.foodCategory,
			'username': user_to_edit.username,
			'gender': user_to_edit.userprofile.gender,
		})

	context = {'form': form, 'is_admin_editing': is_admin_editing}
	if is_admin_editing and user_id:
		return redirect('viewuserprofile', user_id=user_id)
	else:
		return redirect('profile')

@login_required
def update_business_profile(request, user_id=None):
	# Check if the user is an admin and a user_id is provided
	is_admin_editing = user_id is not None and UserType.objects.get(user=request.user).userType == 'admin'

	# If admin is editing, get the user instance to be edited; otherwise, use the request.user instance
	user_to_edit = User.objects.get(id=user_id) if is_admin_editing else request.user

	if request.method == 'POST':
		form = BusinessUpdateForm(request.POST)
		print("Form errors: ", form.errors, flush=True)
		if form.is_valid():
			user_to_edit.first_name = form.cleaned_data['first_name']
			user_to_edit.last_name = form.cleaned_data['last_name']
			user_to_edit.email = form.cleaned_data['email']
			user_to_edit.username = form.cleaned_data['username']
			user_to_edit.save()
			if form.cleaned_data['password']:
				user_to_edit.set_password(form.cleaned_data['password'])
			user_to_edit.save()

			# If admin is editing, update the is_active status
			if is_admin_editing:
				is_active = request.POST.get('is_active') != 'on'
				user_to_edit.is_active = is_active
				user_to_edit.save()
			else:
				if form.cleaned_data['password']:
					login(request, user_to_edit)

			business_profile, created = BusinessProfile.objects.get_or_create(user=user_to_edit)
			business_profile.companyName = form.cleaned_data['company_name']
			business_profile.phone = form.cleaned_data['phone']
			business_profile.address = form.cleaned_data['address']
			business_profile.postalCode = form.cleaned_data['postal_code']
			business_profile.foodCategory = form.cleaned_data['food_category']
			business_profile.save()

			# If admin is editing, update the is_active status
			if is_admin_editing:
				is_verified = request.POST.get('is_verified') == 'on'
				business_profile.isVerified = is_verified
				business_profile.save()

			messages.success(request, 'Business profile has been updated successfully.')
			if is_admin_editing and user_id:
				return redirect('viewbusinessprofile', user_id=user_id)
			else:
				return redirect('profile')
		else:
			messages.error(request, 'There was an error in updating the business profile. Please check your input(s).')
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

	context = {'form': form, 'is_admin_editing': is_admin_editing}
	if is_admin_editing and user_id:
		return redirect('viewbusinessprofile', user_id=user_id)
	else:
		return redirect('profile')

@login_required
def update_admin_profile(request):
	if request.method == 'POST':
		first_name = request.POST['first_name']
		last_name = request.POST['last_name']
		email = request.POST['email']
		username = request.POST['username']
		password = request.POST['password']

		# Update the user's information
		user = request.user
		user.first_name = first_name
		user.last_name = last_name
		user.email = email
		user.username = username

		# Update the password only if it's not empty
		if password:
			user.set_password(password)
			login(request, request.user)

		user.save()

		messages.success(request, 'Your profile has been updated successfully.')
		return redirect('updateadmin')  # Replace with the URL name for your update admin page

	context = {
		'user': request.user,
	}
	return redirect('profile')

@login_required
def create_promotion(request):
	user_type = UserType.objects.get(user=request.user)
	if request.method == 'POST':
		form = PromotionForm(request.POST)
		if form.is_valid():
			promotion = form.save(commit=False)
			promotion.createdBy = request.user
			promotion.isActive = promotion.startDate <= timezone.now().date() <= promotion.endDate
			promotion.save()
			messages.success(request, 'Promotion has been created successfully.')
			return redirect('businesshome')
		else:
			messages.error(request, 'There was an error in creating the promotion. Please check your input(s).')
	else:
		form = PromotionForm()
	context = {
		'form':form,
		'user_type':user_type,
	}
	return render(request, 'createpromotion.html', context)


# @login_required
# def promotion_list(request):
#     now = timezone.now().date()
#     promotions = Promotion.objects.filter(endDate__gte=now).order_by('startDate')
#     context = {
#         'promotions': promotions,
#     }
#     return render(request, 'promotion_list.html', context)

@login_required
def search_promotion(request):
	user_type = UserType.objects.get(user=request.user)
	promotions = Promotion.objects.all()
	if user_type.userType in ['user','business']:
		promotions = Promotion.objects.filter(isActive=True)
	else:
		promotions = Promotion.objects.all()
	print("zx promotions: "+str(promotions),flush=True)
	context = {'user_type': user_type, 'promotions':promotions}
	return render(request, 'searchpromotion.html', context)