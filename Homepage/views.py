from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib import messages
from .models import FoodCategory
from .forms import FoodCategoryForm

import sys


def home(request):
	return render(request, 'home.html', {})

def about(request):
	return render(request, 'about.html', {})

def login_user(request):
	if request.method == 'POST':
	    username = request.POST['username']
	    password = request.POST['password']
	    user = authenticate(request, username=username, password=password)
	    if user is not None:
	        login(request, user)
	        messages.success(request,('Login succesful!'))
	        return redirect('home')
	    else:
	    	messages.error(request,('Login unsuccesful! Please try again!'))
	    	return redirect('login')
	else:

		return render(request, 'login.html', {})

def logout_user(request):
    logout(request)
    messages.success(request, ('Logout succesful!'))
    return redirect('home')

def user_profile(request):
	return render(request, 'userprofile.html', {})

def register(request):
	return render(request, 'register.html', {})

def register_user(request):
	foodCategory = FoodCategory.objects.all()
	return render(request, 'registeruser.html', {'foodCategory':foodCategory})

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
		print('zx1')
		print(form)
		sys.stdout.flush()

		if form.is_valid():
			print('zx2')
			sys.stdout.flush()
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
