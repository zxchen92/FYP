from django.urls import path
from . import views

urlpatterns = [
	path('',views.home, name="home"),
	path('about',views.about, name="about"),
	path('login',views.login_user, name="login"),
	path('logout',views.logout_user, name='logout'),
	path('/userprofile',views.user_profile, name='profile'),
	path('/register',views.register, name='register'),
	path('/register/user',views.register_user, name='registeruser'),
	path('/register/business',views.register_business, name='registerbusiness'),
]