import os

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'fyp.settings')
import django

django.setup()

from django.contrib.auth.models import User
from Homepage.models import UserProfile, UserType, Rating

# Delete all ratings for the clone users
Rating.objects.filter(user__username__startswith='cloneusers').delete()

# Delete all users
User.objects.filter(username__startswith='cloneusers').delete()

# Delete all user profiles
UserProfile.objects.filter(user__username__startswith='cloneusers').delete()

# Delete all user types
UserType.objects.filter(user__username__startswith='cloneusers').delete()

print('All test users have been deleted.')
