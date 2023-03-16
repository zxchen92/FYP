from django.contrib import admin
from .models import FoodCategory, UserType, UserProfile, BusinessProfile

# Register your models here.
admin.site.register(FoodCategory)
admin.site.register(UserType)
admin.site.register(UserProfile)
admin.site.register(BusinessProfile)