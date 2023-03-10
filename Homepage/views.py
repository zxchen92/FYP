from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages


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