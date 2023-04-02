from django.urls import path
from . import views

urlpatterns = [
	path('',views.landing, name="landing"),
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
	path('administrative/home',views.admin_home,name='adminhome'),
	path('registeredbusinesses',views.registered_businesses ,name='registeredBusinesses'),
	path('userhome',views.user_home ,name='userhome'),
	path('businesshome',views.business_home ,name='businesshome'),
	path('searchusers',views.search_users ,name='searchusers'),
	path('userpromotion',views.user_promotion ,name='userpromotion'),
	path('recommenderresults',views.recommender_results ,name='recommenderresults'),
	path('viewuserprofile',views.view_user_profile ,name='viewuserprofile'),
	path('viewbusinessprofile',views.view_business_profile ,name='viewbusinessprofile'),
	path('recommenderresults/rate',views.create_rating, name='rate'),
	path('foodquiz',views.food_quiz, name ='foodquiz'),
]