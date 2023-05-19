import os
import random

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'fyp.settings')
import django

django.setup()

from django.contrib.auth.models import User
from Homepage.models import UserProfile, UserType, FoodCategory, Food, Rating

# Get the list of food categories
food_categories = FoodCategory.objects.all()
food = Food.objects.all()

# Create new users
for i in range(200):
    # Generate a random username
    username = f'cloneusers{i}'
    password = 'test'

    # Create a new user object
    user = User.objects.create_user(username=username, password=password)

    # Create a new user profile
    birth_year = random.randint(1951, 2003)
    birth_month = random.randint(1, 12)
    birth_day = random.randint(1, 28)
    birthdate = f'{birth_year}-{birth_month:02}-{birth_day:02}'
    phone = f'{random.randint(10000000, 99999999):08}'
    fav_food = random.choice(food).foodName
    pref_location = random.choice(['1', '2', '3', '4', '5'])
    food_category = random.choice(food_categories)
    num_restrictions = random.randint(0, 3)
    dietary_restrictions = list(set([random.choice(UserProfile.DIETARY_RESTRICTIONS)[0] for i in range(num_restrictions)]))
    dietary_restrictions_str = ', '.join(filter(None, dietary_restrictions))
    gender = random.choice(['M', 'F'])
    user_profile = UserProfile.objects.create(user=user, birthdate=birthdate, phone=phone, favFood=fav_food, prefLocation=pref_location, foodCategory=food_category, dietary_restrictions=dietary_restrictions_str, gender=gender)

    # Create a user type
    user_type = UserType.objects.create(user=user, userType='user')

    print(f'Created user {username} with password {password}')

    # Add 10 ratings for the user
    for j in range(10):
        rating = random.randint(1, 5)
        food_item = random.choice(food).foodName
        Rating.objects.create(user=user, food=food_item, rating=rating)

    print(f'Added 10 ratings for user {username}')