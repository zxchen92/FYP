from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from .models import FoodCategory
from .forms import FoodCategoryForm


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
	return render(request, 'registeruser.html', {})

def register_business(request):
	return render(request, 'registerbusiness.html', {})

def food_category(request):

	foodCategory = FoodCategory.objects.all()

	return render(request, 'foodcategory.html', {'foodCategory':foodCategory})

def add_food_category(request):
	if request.method == 'POST':
		form = FoodCategoryForm(request.POST or None)
		print(form)

		# if form.is_valid():
		# 	form.save()
		# 	messages.success(request, ("Food Category has been added!"))
		# 	return redirect(food_category)

	return redirect(food_category)

def delete_food_category(request):
	return redirect(food_category)