from django.contrib import admin
from .models import FoodCategory, Rating, UserType, UserProfile, BusinessProfile
from django.contrib.auth.models import User
from django.contrib.auth.admin import UserAdmin as DefaultUserAdmin

class UserAdmin(DefaultUserAdmin):
    list_display = ('id', 'username', 'email', 'first_name', 'last_name', 'is_staff')


# Register your models here.
admin.site.unregister(User)
admin.site.register(User, UserAdmin)
admin.site.register(FoodCategory)
admin.site.register(UserType)
admin.site.register(UserProfile)
admin.site.register(BusinessProfile)
admin.site.register(Rating)
