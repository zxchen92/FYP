from django.urls import path
from . import views

urlpatterns = [
	path('',views.home, name="home"),
	path('about',views.about, name="about"),
	path('login',views.login_user, name="login"),
	path('logout',views.logout_user, name='logout'),
	path('userprofile',views.user_profile, name='profile'),
	path('register',views.register, name='register'),
	path('register/user',views.register_user, name='registeruser'),
	path('register/business',views.register_business, name='registerbusiness'),
	path('administrative/foodcategory',views.food_category, name='foodcategory'),
	path('administrative/addfoodcategory',views.add_food_category, name='addfoodcategory'),
	path('administrative/deletefoodcategory/<food_category_id>',views.delete_food_category, name='deletefoodcategory'),
	path('recommender',views.recommender_page,name='recommenderpage'),
	path('customersupport',views.customer_support,name='customersupport'),
]