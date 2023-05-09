from django.urls import path
from . import views

urlpatterns = [
	path('',views.landing, name="landing"),
	path('about',views.about, name="about"),
	path('administrative/addfoodcategory',views.add_food_category, name='addfoodcategory'),
	path('administrative/deletefoodcategory/<food_category_id>',views.delete_food_category, name='deletefoodcategory'),
	path('administrative/foodcategory',views.food_category, name='foodcategory'),
	path('administrative/home',views.admin_home,name='adminhome'),
	path('businesshome',views.business_home ,name='businesshome'),
	path('customersupport',views.customer_support,name='customersupport'),
	path('createpromotion',views.create_promotion,name='createpromotion'),
	path('datainsights', views.data_insight, name='datainsights'),
	path('deletepromotion/<promotion_id>', views.delete_promotion, name='deletepromotion'),
    path('delete_promotion2/<int:promotion_id>/', views.delete_promotion2, name='delete_promotion2'),
	path('foodquiz',views.food_quiz, name ='foodquiz'),
	path('login',views.login_user, name="login"),
	path('logout',views.logout_user, name='logout'),
	path('recommender',views.recommender_page,name='recommenderpage'),
	path('recommendernormal',views.recommender_normal ,name='recommendernormal'),
	path('recommenderresults',views.recommender_results ,name='recommenderresults'),
	path('recommenderresults/rate',views.create_rating, name='rate'),
	path('register/business',views.register_business, name='registerbusiness'),
	path('register/user',views.register_user, name='registeruser'),
	path('searchbusinesses',views.search_businesses,name='searchbusinesses'),
	path('searchpromotions',views.search_promotion,name='searchpromotions'),
	path('searchusers',views.search_users ,name='searchusers'),
	path('updateadmin',views.update_admin_profile, name ='updateadmin'),
	path('updatebusiness',views.update_business_profile, name ='updatebusiness_self'),
	path('updatebusiness/<int:user_id>/',views.update_business_profile, name ='updatebusiness'),
	path('updatepromotion/<int:promotion_id>', views.update_promotion, name = 'updatepromotion'),
	path('updateuser',views.update_user_profile, name ='updateuser_self'),
	path('updateuser/<int:user_id>/', views.update_user_profile, name='updateuser'),
	path('userhome/',views.user_home,name='userhome'),
	path('userprofile',views.user_profile, name='profile'),
	path('viewbusinessprofile/<int:user_id>/',views.view_business_profile ,name='viewbusinessprofile'),
	path('viewpromotion/<int:promotion_id>/',views.view_promotion ,name='viewpromotion'),
	path('viewratings', views.view_ratings, name='viewratings'),
	path('viewuserprofile/<int:user_id>/', views.view_user_profile, name='viewuserprofile'),
    path('datacrawler', views.data_crawler_page, name='datacrawler'),
    path('dataplacecrawler', views.place_crawler, name='dataplacecrawler'),
    path('datareviewcrawler', views.review_crawler, name='datareviewcrawler'),

]