from django.contrib import admin
from .models import FoodCategory, Rating, UserType, UserProfile, BusinessProfile

# Register your models here.
admin.site.register(FoodCategory)
admin.site.register(UserType)
admin.site.register(UserProfile)
admin.site.register(BusinessProfile)
admin.site.register(Rating)