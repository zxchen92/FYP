from pickle import TRUE
import re
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404
from django.core.mail import send_mail
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail

from django.db import IntegrityError
from django.db.models import Count

from .models import Rating, Food
from .data_insights import data_insights
from django.utils import timezone
import matplotlib.pyplot as plt
import io
import base64
import csv
import numpy as np
import pandas as pd
import tensorflow as tf
import sklearn
from sklearn.preprocessing import MinMaxScaler

from .data_review_crawler import data_review_crawler
from .data_place_crawler import data_place_crawler

from .food_recommender import get_recommendations
from .models import FoodCategory,UserProfile,UserType,BusinessProfile,Rating,Food,Promotion
from .forms import UserRegistrationForm,BusinessRegistrationForm,FoodCategoryForm,RatingForm,UserUpdateForm,BusinessUpdateForm,PromotionForm,FoodForm

from datetime import date
from datetime import datetime


import sys
import os

sendgrid_api_key = os.environ.get('SENDGRID_API_KEY')

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

DIETARY_RESTRICTIONS_OPTIONS = [
	('vegetarian', 'Vegetarian'),
	('halal', 'Halal'),
	('seafood_free', 'Seafood-Free'),
]

def landing(request):
	context = {}
	if request.user.is_authenticated:
		user_type = UserType.objects.get(user=request.user)
		context = {'user_type': user_type}
	user_count = UserType.objects.filter(userType='user').count()
	business_count = UserType.objects.filter(userType='business').count()
	context['user_count'] = user_count
	context['business_count'] = business_count
	return render(request, 'landing.html', context)

def about(request):
	context = {}
	if request.user.is_authenticated:
		user_type = UserType.objects.get(user=request.user)
		context = {'user_type': user_type}
	return render(request, 'about.html', context)

# def login_user(request):
# 	if request.method == 'POST':
# 		username = request.POST['username']
# 		password = request.POST['password']
# 		user = authenticate(request, username=username, password=password)
# 		if user is not None:
# 			login(request, user)
# 			messages.success(request,('Login succesful!'))
# 			user_type = get_object_or_404(UserType, user=user)
# 			if user_type.userType == 'admin':
# 				return redirect('adminhome')
# 			elif user_type.userType == 'user':
# 				return redirect('userhome')
# 			else:
# 				return redirect('businesshome')
# 		else:
# 			messages.error(request,('Login unsuccesful! Please try again!'))
# 			print(f"Authentication error: {request.session.get('django.contrib.auth.error_messages')}",flush=True)

# 			return redirect('login')
# 	else:
# 		return render(request, 'login.html', {})

from django.contrib import messages
from django.contrib.auth.forms import AuthenticationForm

def login_user(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            messages.success(request, 'Login successful!')
            user_type = get_object_or_404(UserType, user=user)
            if user_type.userType == 'admin':
                return redirect('adminhome')
            elif user_type.userType == 'user':
                return redirect('userhome')
            else:
                return redirect('businesshome')
        else:
            form = AuthenticationForm(request, data=request.POST)
            if form.is_valid():
                messages.error(request, 'Login unsuccessful! Please try again!')
            else:
                error_message = form.errors.get_json_data(escape_html=True)
                messages.error(request, error_message)
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
			dietary_restrictions = [dict(UserProfile.DIETARY_RESTRICTIONS)[value] for value in user_profile.dietary_restrictions]
			context = {
				'foodCategory':foodCategory,
				'user_type':user_type,
				'user_profile':user_profile,
				'location_options': location_options,
				'gender_options':gender_options,
				'DIETARY_RESTRICTIONS_OPTIONS':DIETARY_RESTRICTIONS_OPTIONS,
				'dietary_restrictions':dietary_restrictions,
			}
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
	form = UserRegistrationForm(request.POST or None)  # Pass POST data to the form if it exists
	checked_dietary_restrictions = []

	if request.method == 'POST':
		print("Form errors: ", form.errors, flush=True)
		checked_dietary_restrictions = request.POST.getlist('dietary_restrictions')
		if form.is_valid():
			try:
				# Save user, user_profile, and user_type
				user, user_profile, user_type = form.save(commit=False)
				# Set user attributes
				user.first_name = request.POST.get('first_name')
				user.last_name = request.POST.get('last_name')
				user.email = request.POST.get('email')
				user.username = request.POST.get('username')
				user.password = request.POST.get('password')
				user.save()
				# Set user_profile attributes
				user_profile.birthdate_str = request.POST.get('birthdate')
				user_profile.gender = request.POST.get('gender')
				user_profile.phone = request.POST.get('phone')
				user_profile.favorite_food = request.POST.get('favorite_food')
				user_profile.preferred_location = request.POST.get('preferred_location')
				user_profile.food_category_id = request.POST.get('food_category')
				user_profile.dietary_restrictions = request.POST.getlist('dietary_restrictions')
				user_profile.user = user
				user_profile.save()
				# Set user_type attributes
				user_type.user = user
				user_type.save()

				if user is not None:
					login(request, user)
					messages.success(request, 'User registered!')
					return redirect('userhome')
			except IntegrityError:
				# Catch the IntegrityError exception raised by trying to create a user with an existing username
				messages.error(request, 'Username already exists. Please choose a different username.')
				form.add_error('username', 'Username already exists. Please choose a different username.')
		else:
			messages.error(request, 'User registration unsuccessful! Please try again!')

	context = {
		'checked_dietary_restrictions':checked_dietary_restrictions,
		'foodCategory': foodCategory,
		'form': form,
		'location_options': location_options,
		'gender_options': gender_options,
		'DIETARY_RESTRICTIONS_OPTIONS': DIETARY_RESTRICTIONS_OPTIONS,
	}
	return render(request, 'registeruser.html', context)

def register_business(request):
	foodCategory = FoodCategory.objects.all()
	form = BusinessRegistrationForm(request.POST)
	if request.method == 'POST':
		print("Form errors: ", form.errors, flush=True)
		if form.is_valid():
			user, business_profile, user_type = form.save(commit=False)

			user.first_name = request.POST.get('first_name')
			user.last_name = request.POST.get('last_name')
			user.email = request.POST.get('email')
			user.username = request.POST.get('username')
			user.password = request.POST.get('password')

			business_profile.companyName = request.POST.get('company_name')
			business_profile.phone = request.POST.get('phone')
			business_profile.address = request.POST.get('address')
			business_profile.postalCode = request.POST.get('postal_code')
			business_profile.food_category_id = request.POST.get('food_category')

			user.is_active = False
			print('user.username:',user.username, flush=True)
			print('user.password:',user.password, flush=True)
			user.set_password(form.cleaned_data['password'])
			user.save()
			business_profile.user = user
			business_profile.save()
			user_type.user = user
			user_type.userType = 'business'
			user_type.save()
			if user is not None:
				messages.success(request, ('Business registered! We will notify you when your business is verfied!'))
				return redirect('landing')
		else:
			messages.error(request,('User registration unsuccesful! Please try again!'))
			form = BusinessRegistrationForm()

	context = {
		'foodCategory':foodCategory,
		'form':form,
	}
	return render(request, 'registerbusiness.html', context)

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
		user = request.user
		user_type = UserType.objects.get(user=user)
		context = {
			'user_type': user_type,
			'user': user,
			}
	if request.method == 'POST':
		first_name = request.POST.get('firstName')
		last_name = request.POST.get('lastName')
		email = request.POST.get('email')
		category = request.POST.get('category')
		details = request.POST.get('details')
		print("first_name: ",first_name)
		message_content = f"Customer Support Request:\n\nName: {first_name} {last_name}\nEmail: {email}\nCategory: {category}\nDetails: {details}"

		messages.success(request, ('An email has been sent to our customer support officers! We will get back to you within 3 working days.'))

		message = Mail(
			from_email='customersup.collabfood@outlook.com',
			to_emails=['customersup.collabfood@outlook.com', email],
			subject='New Customer Support Request',
			plain_text_content=message_content)

		try:
			print('sendgrid_api_key',sendgrid_api_key,flush=True)
			sg = SendGridAPIClient(sendgrid_api_key) 
			response = sg.send(message)
			print('response: ',response,flush=True)
		except Exception as e:
			print(str(e))

		return redirect(landing)

	return render(request, 'customersupport.html', context)

@login_required
def admin_home(request):
	user_type = UserType.objects.get(user=request.user)
	business_count = UserType.objects.filter(userType='business').count()
	user_count = UserType.objects.filter(userType='user').count()
	businesses = BusinessProfile.objects.filter(isVerified=False)
	not_verified_count = businesses.count()
	context = {
		'user_type': user_type,
		'businesses':businesses,
		'not_verified_count':not_verified_count,
		'business_count': business_count,
		'user_count': user_count,
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
    readonly = ''
    if user_type.userType == "user":
        readonly = "readonly"
    promotion = Promotion.objects.filter(isActive=True, endDate__gte=timezone.now()).order_by('-createdDate').first()
    context = {
        'user_type': user_type,
        'promotion': promotion,
        'readonly': readonly,
    }
    return render(request, 'userhome.html', context)

@login_required
def business_home(request):
	user_type = UserType.objects.get(user=request.user)
	context = {'user_type': user_type}
	return render(request, 'businesshome.html', context)

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
	readonly = ''
	if user_type.userType == "user":
		readonly = "readonly"
	context = {
		'user_type': user_type,
		'users':users,
		'promotion':promotion,
		'readonly': readonly,
		}
	return render(request, 'viewpromotion.html', context)

@login_required
def recommender_results(request):
	user_id = request.user.id
	recommendations, recommendationsTwo = get_recommendations(user_id)
	profile = UserProfile.objects.get(user=request.user)
	diet = profile.dietary_restrictions
	print(diet)

	user_type = UserType.objects.get(user=request.user)
	form = RatingForm(request.POST)

	context = {
	'user_type': user_type,
	'form': form,
	'diet' : diet,
	}

	ratings = Rating.objects.filter(user=request.user).values('food')
	rating_count = ratings.distinct().count()


	if rating_count > 10 :
		food_dict = {}

		for foodid in recommendations:
			food_dict[foodid] = get_object_or_404(Food, id=foodid)

		remove_ids = []  # list to store food IDs to be removed
		for food_id, food in food_dict.items():
			if not all(d in food.dietary_restrictions for d in diet):
				remove_ids.append(food_id)
		# Remove the food IDs that don't meet the dietary restrictions
		for food_id in remove_ids:
			del food_dict[food_id]
		
		print("food dictbefore itr" + str(food_dict) , flush= True)
		predicted_highest_rating_food = next(iter(food_dict))
		print("HIGHSET FOOD" + str(predicted_highest_rating_food), flush=True)
		remove_keys = []
		for key in food_dict.keys():
			if key != predicted_highest_rating_food :
				remove_keys.append(key)
		for key in remove_keys:
			del food_dict[key]
			print(str(food_dict))
		
		print("food dict" + str(food_dict) , flush= True)

		context['recommendations'] =  food_dict

	else:
		food_dict={}
		for foodid in recommendationsTwo:
			try:
				food2 =  get_object_or_404(Food, id=foodid)
				if all(d in food2.dietary_restrictions for d in diet):
					food_dict[foodid] = food2
			except Food.DoesNotExist:
				pass
		context['recommendations'] = food_dict

	return render(request, 'recommenderresults.html',context)

@login_required
def recommender_normal(request):
	user_id = request.user.id
	user_profile = UserProfile.objects.get(user=request.user)
	recommendations, recommendationsTwo = get_recommendations(user_id)

	food_category = request.POST.get('food-category')
	food_category_name = get_object_or_404(FoodCategory, id=food_category).categoryName

	print(food_category)

	user_type = UserType.objects.get(user=request.user)
	form = RatingForm(request.POST)
	
	context = {
	'user_type': user_type,
	'form': form,
	'food_category' : food_category,
	'food_category_name': food_category_name,
	'user_profile' : user_profile,
	}


	food_dict={}
	for foodid in recommendationsTwo:
		try:
			category = get_object_or_404(FoodCategory, id=food_category)
			food2 =  get_object_or_404(Food, id=foodid)
			if category.categoryName in food2.foodCategory.categoryName:
				food_dict[foodid] = food2
		except Food.DoesNotExist:
			pass
	###################### Recommender by age #############################
	# Get current year and user's age
	now = datetime.now()
	current_year = now.year
	user_profiles = get_object_or_404(UserProfile, user=request.user)
	user_age = current_year - user_profiles.birthdate.year

	# Get all users and their age groups
	users = UserProfile.objects.all()
	age_groups = [(current_year - user.birthdate.year) // 10 for user in UserProfile.objects.all()]

	# Find the index of the current user within the queryset
	user_index = list(users).index(request.user.userprofile)

	# Determine the user's age group
	user_age_group = age_groups[user_index]

	# Get most rated food data
	food_ratings_count = Rating.objects.values('food').annotate(count=Count('food')).order_by('-count')
	food_names = [fr['food'] for fr in food_ratings_count]
	food_counts_all = [fr['count'] for fr in food_ratings_count]

	# Create dictionary to store food counts for each age group
	food_counts = {}
	for age_group in age_groups:
		food_counts[age_group] = {}
		for food in food_ratings_count:
			ratings = Rating.objects.filter(food=food['food'], 
											user__userprofile__birthdate__year__lte=current_year-age_group*10, 
											user__userprofile__birthdate__year__gt=current_year-(age_group+1)*10)
			food_counts[age_group][food['food']] = ratings.count()

	# Determine most popular food for the user's age group
	food_counts_age_group = food_counts[user_age_group]
	food_counts_age_group_sorted = sorted(food_counts_age_group.items(), key=lambda x: x[1], reverse=True)

	# Create list of recommended food objects
	recommended_food = []
	currentUserRatings = []
	currentUserRatings = Rating.objects.filter(user=request.user)
	print("current user rating is " + str(currentUserRatings), flush=True)
	
	for food_count in food_counts_age_group_sorted:
		foods = Food.objects.get(foodName=food_count[0])
		print("foods " + str(foods), flush=True)
		#if food not in request.user.ratings.all():
		if not currentUserRatings.filter(food=foods).exists():
			recommended_food.append(foods)
			if len(recommended_food) >= 100:
				break
	food_dict2={}
	for foodid in recommended_food:
		try:
			print("foodid" + str(foodid), flush=True)
			category = get_object_or_404(FoodCategory, id=food_category)
			food3 =  foodid #get_object_or_404(Food, foodid)
			print("food3" + str(food3), flush=True)
			if category.categoryName in food3.foodCategory.categoryName:
				food_dict2[foodid] = food3
		except Food.DoesNotExist:
			pass
	########################################################################
	print("This is the food_dict2" + str(food_dict2), flush=True)
	context['recommendations'] = food_dict
	context['recommendationsByAge'] = food_dict2
	return render(request, 'nomlrecommender.html',context)


@login_required
def view_user_profile(request, user_id):
	selected_user = User.objects.get(id=user_id)
	selected_user_profile  = UserProfile.objects.get(user=selected_user)
	user_type = UserType.objects.get(user=request.user)
	foodCategory = FoodCategory.objects.all()
	dietary_restrictions = [dict(UserProfile.DIETARY_RESTRICTIONS)[value] for value in selected_user_profile.dietary_restrictions]
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
		'DIETARY_RESTRICTIONS_OPTIONS':DIETARY_RESTRICTIONS_OPTIONS,
		'dietary_restrictions':dietary_restrictions,
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
	if request.method == 'POST':
		user = request.user
		food = request.POST.get('food', '')
		rating_value = request.POST.get('rating', None)

		if rating_value is not None:
			rating_value = int(rating_value)
			if 1 <= rating_value <= 5:
				rating, created = Rating.objects.get_or_create(user=user, food=food, defaults={'rating': rating_value})
				rating.rating = rating_value
				rating.save()
				messages.success(request, ('Successfully rated! We will take this rating into account in your next reccomendation!'))
				return redirect(user_home)
		else:
			messages.error(request,('Please select a rating and try again!'))
	return redirect(request, 'recommenderresults.html')

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
			user_profile.birthdate = form.cleaned_data['birthdate']
			user_profile.phone = form.cleaned_data['phone']
			user_profile.favFood = form.cleaned_data['favorite_food']
			user_profile.prefLocation = form.cleaned_data['preferred_location']
			user_profile.foodCategory = form.cleaned_data['food_category']
			user_profile.gender = form.cleaned_data['gender']
			user_profile.dietary_restrictions = form.cleaned_data['dietary_restrictions']
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
			'birthdate': user_to_edit.userprofile.birthdate,
			'email': user_to_edit.email,
			'phone': user_to_edit.userprofile.phone,
			'favorite_food': user_to_edit.userprofile.favFood,
			'preferred_location': user_to_edit.userprofile.prefLocation,
			'food_category': user_to_edit.userprofile.foodCategory,
			'username': user_to_edit.username,
			'gender': user_to_edit.userprofile.gender,
			'dietary_restrictions': user_to_edit.userprofile.dietary_restrictions
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
			if form.cleaned_data['password']:
				user_to_edit.set_password(form.cleaned_data['password'])
			
			# If admin is editing, update the is_active status
			if is_admin_editing:
				is_active = request.POST.get('is_active') != 'on'
				user_to_edit.is_active = is_active

			user_to_edit.save()

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
			print('user_to_edit.username:',user_to_edit.username, flush=True)
			print('user_to_edit.password:',user_to_edit.password, flush=True)
			messages.success(request, 'Business profile has been updated successfully.')
			if is_admin_editing and user_id:
				return redirect(search_businesses)
			else:
				return redirect(business_home)
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
		return redirect(search_businesses)
	else:
		return redirect(business_home)

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
		return redirect('updateadmin')

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
			# promotion.isActive = promotion.startDate <= timezone.now().date() <= promotion.endDate
			promotion.save()
			messages.success(request, 'Promotion has been created successfully.')
			return redirect('searchpromotions')
		else:
			messages.error(request, 'There was an error in creating the promotion. Please check your input(s).')
	else:
		form = PromotionForm()
	context = {
		'form':form,
		'user_type':user_type,
	}
	return render(request, 'createpromotion.html', context)

@login_required
def update_promotion(request, promotion_id=None):
	is_admin_editing = UserType.objects.get(user=request.user).userType == 'admin'
	promotion_to_edit = Promotion.objects.get(id=promotion_id)
	user_type = UserType.objects.get(user=request.user)
	if request.method == 'POST':
		form = PromotionForm(request.POST, instance=promotion_to_edit)
		if form.is_valid():
			promotion_to_edit = form.save(commit=False)
			if is_admin_editing:
				is_active = request.POST.get('is_active') != 'on'
				promotion_to_edit.isActive = is_active
			promotion_to_edit.save()
			messages.success(request, 'Promotion has been updated successfully.')
			return redirect('searchpromotions')
		else:
			messages.error(request, 'There was an error in updating the promotion. Please check your input(s).')
	else:
		form = PromotionForm(instance=promotion_to_edit)
	context = {
		'form': form,
		'user_type': user_type,
		'promotion': promotion_to_edit
	}
	return render(request, 'viewpromotion.html', context)

@login_required
def search_promotion(request):
	user_type = UserType.objects.get(user=request.user)
	promotions = Promotion.objects.all()
	if user_type.userType in ['user']:
		promotions = Promotion.objects.filter(isActive=True, endDate__gte=timezone.now())
	elif user_type.userType in ['business']:
		promotions = Promotion.objects.filter(createdBy = request.user)
	else:
		promotions = Promotion.objects.all()
	print("zx promotions: "+str(promotions),flush=True)
	context = {'user_type': user_type, 'promotions':promotions}
	return render(request, 'searchpromotion.html', context)

@login_required
def delete_promotion(request, promotion_id):
	item = Promotion.objects.get(pk=promotion_id)
	item.delete()
	messages.success(request,("Promotion Deleted!"))
	return redirect(search_promotion)

@login_required
def data_insight(request):
	user_type = UserType.objects.get(user=request.user)
	if user_type.userType in ['user','business']:

		image_data1 , image_data2, image_data3, image_data4, image_data5, image_data6 = data_insights()

		context = {
		'user_type': user_type,
		'image_data1':image_data1,
		'image_data2' : image_data2,
		'image_data3' : image_data3,
		'image_data4' : image_data4,
		'image_data5' : image_data5,
		'image_data6' : image_data6,
		}
	return render(request, 'datainsights.html', context)

@login_required
def view_ratings(request):
	user = request.user
	ratings = Rating.objects.filter(user=user)
	user_type = UserType.objects.get(user=request.user)
	rating_values = [(rating, range(1, rating.rating+1), range(rating.rating+1, 6)) for rating in ratings]
	context = {
		'rating_values': rating_values,
		'user_type': user_type
	}
	return render(request, 'viewratings.html', context)

def create_stars(rating):
	full_stars = int(rating)
	half_stars = 1 if (rating - full_stars) >= 0.5 else 0
	empty_stars = 5 - full_stars - half_stars
	return ' '.join(['<span class="fa fa-star checked"></span>' for _ in range(full_stars)] +
					['<span class="fa fa-star-half-o checked"></span>'] * half_stars +
					['<span class="fa fa-star"></span>'] * empty_stars)

@login_required
def data_crawler_page(request):
	user_type = UserType.objects.get(user=request.user)

	if user_type.userType in ['user','admin']:

		context = {
			'user_type':user_type,
		}
		return render(request, 'datacrawler.html', context)

@login_required
def place_crawler(request):
	user_type = UserType.objects.get(user=request.user)

	if 	user_type.userType in ['user', 'admin']:
		try:
			dfPlace, messageTwo = data_place_crawler()
			context = {
				'user_type': user_type,
				'dfPlace': dfPlace,
				'messageTwo': messageTwo,
			}
		except Exception as e:
			context = {
				'user_type': user_type,
				'error': str(e),
			}

		return render(request,'dataplacecrawler.html', context)

@login_required
def review_crawler(request):
	user_type = UserType.objects.get(user=request.user)

	if 	user_type.userType in ['user', 'admin']:
		try:
			messageTwo = data_review_crawler()
			context = {
				'messageTwo': messageTwo,
			}
		except Exception as e:
			context = {
				'user_type': user_type,
				'error': str(e),
			}
		return render(request,'datareviewcrawler.html', context)

@login_required
def search_food(request):
	user_type = UserType.objects.get(user=request.user)
	food = Food.objects.all()
	context = {'user_type': user_type, 'food':food}
	return render(request, 'searchfood.html', context)

@login_required
def create_food(request):
	foodCategory = FoodCategory.objects.all()
	user_type = UserType.objects.get(user=request.user)
	checked_dietary_restrictions = []
	form = FoodForm(request.POST or None)
	if request.method == 'POST':
		print("Form errors: ", form.errors, flush=True)
		checked_dietary_restrictions = request.POST.getlist('dietary_restrictions')
		if form.is_valid():
			food = form.save(commit=False)
			food.foodName = request.POST.get('foodName')
			food.foodCategory = FoodCategory.objects.get(id=request.POST.get('foodCategory'))
			food.save()
			messages.success(request, 'The food has been created successfully.')

			with open('place_url.csv', 'a', newline='') as csvfile:
				writer = csv.writer(csvfile)
				writer.writerow([food.id, f"https://www.google.com/maps/search/{food.foodName.replace(' ', '+')}+in+singapore"])

			return redirect(search_food)
		else:
			messages.error(request, 'There was an error in creating the food. Please check your input(s).')
	else:
		form = FoodForm()
	context = {
		'checked_dietary_restrictions':checked_dietary_restrictions,
		'form':form,
		'user_type':user_type,
		'foodCategory':foodCategory,
		'DIETARY_RESTRICTIONS_OPTIONS':DIETARY_RESTRICTIONS_OPTIONS,
	}
	return render(request, 'createfood.html', context)

@login_required
def delete_food(request, food_id):
	item = Food.objects.get(pk=food_id)
	item.delete()
	messages.success(request,("Food Deleted!"))
	return redirect(search_food)

@login_required
def view_food(request, food_id=None):
	foodCategory = FoodCategory.objects.all()
	users = User.objects.all()
	user_type = UserType.objects.get(user=request.user)
	food = Food.objects.get(id=food_id)
	dietary_restrictions = [dict(UserProfile.DIETARY_RESTRICTIONS)[value] for value in food.dietary_restrictions]
	context = {
		'user_type': user_type,
		'users':users,
		'food':food,
		'foodCategory':foodCategory,
		'dietary_restrictions':dietary_restrictions,
		'DIETARY_RESTRICTIONS_OPTIONS':DIETARY_RESTRICTIONS_OPTIONS,
		}
	return render(request, 'viewfood.html', context)

@login_required
def update_food(request, food_id=None):
	food_to_edit = Food.objects.get(id=food_id)
	user_type = UserType.objects.get(user=request.user)
	if request.method == 'POST':
		form = FoodForm(request.POST, instance=food_to_edit)
		if form.is_valid():
			food_to_edit = form.save(commit=False)
			food_to_edit.foodName = request.POST.get('foodName')
			food_to_edit.foodCategory = FoodCategory.objects.get(id=request.POST.get('foodCategory'))
			food_to_edit.save()
			messages.success(request, 'Food has been updated successfully.')
			return redirect(search_food)
		else:
			messages.error(request, 'There was an error in updating the food. Please check your input(s).')
	else:
		form = FoodForm(instance=food_to_edit)
	context = {
		'form': form,
		'user_type': user_type,
		'food': food_to_edit
	}
	return render(request, 'viewfood.html', context)