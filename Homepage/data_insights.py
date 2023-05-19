import io
import base64
import matplotlib
import matplotlib.pyplot as plt
matplotlib.use('Agg')
import pandas as pd
import numpy as np
from django.db.models import Count
from .models import Rating
from .models import UserProfile
from .models import FoodCategory
from .models import Food
from datetime import date
from datetime import datetime


def data_insights():

    food_rating = pd.read_csv('FoodRatings_v1.csv', sep=',', on_bad_lines='skip', encoding="latin-1")
    rating_count=  food_rating['foodid'].value_counts().nlargest(10)
    

    food_ids= rating_count.index.tolist()
    foods_names = [Food.objects.get(id=food_id).foodName for food_id in food_ids]
    rating_count.index = foods_names

    rating_count.plot.bar(color=['#C0C0C0', '#202020', '#7E909A', '#1C4E80', '#A5D8DD', '#EA6A47', '#48abf1', '#fce3b4'
        , '#F0C0A8', '#ee91ad'])

    plt.title('Top Most Rated Foods')
    plt.ylabel('Number of Ratings')
    plt.xticks(rotation=45, ha='right')
    plt.tight_layout()


    # Save the chart as a PNG image in memory
    buffer = io.BytesIO()
    plt.savefig(buffer, format='png')
    buffer.seek(0)
    combined_ratings = base64.b64encode(buffer.read()).decode('utf-8')
    plt.close()
    buffer.close()


    ################################# Top Rated Foods
    # Get the count of ratings for each food
    food_rating_counts = Rating.objects.values('food').annotate(count=Count('food')).order_by('-count')

    # Get the names of the top 10 most rated foods
    top_foods = [f['food'] for f in food_rating_counts[:10]]
    print(""+ str(top_foods))
   
    # Create a bar chart of the top 10 most rated foods
    counts = [f['count'] for f in food_rating_counts[:10]]
    plt.bar(top_foods, counts,
        color=['#C0C0C0', '#202020', '#7E909A', '#1C4E80', '#A5D8DD', '#EA6A47', '#48abf1', '#fce3b4'
        , '#F0C0A8', '#ee91ad'])
    plt.title('Top Most Rated Foods by Users')
    plt.xlabel('Food Name')
    plt.ylabel('Number of Ratings')
    plt.xticks(rotation=45, ha='right')
    plt.tight_layout()

    # Set the y-axis range
    plt.ylim([0, max(counts) + 1])

    # Save the chart as a PNG image in memory
    buffer = io.BytesIO()
    plt.savefig(buffer, format='png')
    buffer.seek(0)
    most_rated_food_graph = base64.b64encode(buffer.read()).decode('utf-8')
    plt.close()
    buffer.close()

    ################################# Top Food Categories

    favourite_category_count = UserProfile.objects.values('foodCategory').annotate(count=Count('foodCategory')).order_by('-count')

    top_categories = [fC['foodCategory'] for fC in favourite_category_count[:10]]
    print("" + str(top_categories))

    category_names = []
    for category_id in top_categories:
        category = FoodCategory.objects.get(id=category_id)
        category_name = category.categoryName
        category_names.append(category_name)




    # Create a bar chart of the top food categories
    countsOne = [fC['count'] for fC in favourite_category_count[:10]]
    plt.bar(category_names, countsOne, 
        color=['#C0C0C0', '#202020', '#7E909A', '#1C4E80', '#A5D8DD', '#EA6A47', '#A5D8DD'])
    plt.title('Top Food Category')
    plt.xlabel('Food Genre')
    plt.ylabel('Number of Users')
    plt.xticks(rotation=45, ha='right')
    plt.tight_layout()


    # Set the y-axis range
    plt.ylim([0, max(counts) + 1])

    # Save the chart as a PNG image in memory
    buffer = io.BytesIO()
    plt.savefig(buffer, format='png')
    buffer.seek(0)
    favourite_categories_graph = base64.b64encode(buffer.read()).decode('utf-8')
    plt.close()
    buffer.close()

    ################################################ Most popular preferred locations
    pref_location_count = UserProfile.objects.values('prefLocation').annotate(count=Count('prefLocation')).order_by('-count')

    pref_location = [PL['prefLocation'] for PL in pref_location_count[:10]]
    print("" + str(pref_location))

    locations = dict(UserProfile.locations)
    for item in pref_location_count:
        item['prefLocation'] = locations[item['prefLocation']]

    # Create a bar chart of the top 10 most rated foods
    countsPL = [PL['count'] for PL in pref_location_count[:5]]
    labelsPL = [PL['prefLocation'] for PL in pref_location_count[:5]]
    plt.pie(countsPL, labels=labelsPL, autopct='%1.1f%%')
    plt.title('Preferred Location')

    # Save the chart as a PNG image in memory
    buffer = io.BytesIO()
    plt.savefig(buffer, format='png')
    buffer.seek(0)
    pref_location_graph = base64.b64encode(buffer.read()).decode('utf-8')
    plt.close()
    buffer.close()

    ################################################ Gender
    gender_count = UserProfile.objects.values('gender').annotate(count=Count('gender')).order_by('-count')

    gender = [g['gender'] for g in gender_count[:10]]
    print("" + str(pref_location))

    # Create a pie chart for gender
    countsG = [g['count'] for g in gender_count[:2]]

    #add colors
    colors = ['#007fbf', 'pink']
    plt.pie(countsG, labels=gender, autopct='%1.1f%%', colors=colors)
    plt.title('Gender')


    # Save the chart as a PNG image in memory
    buffer = io.BytesIO()
    plt.savefig(buffer, format='png')
    buffer.seek(0)
    gender_graph = base64.b64encode(buffer.read()).decode('utf-8')
    plt.close()
    buffer.close()

    ############################################### Age group
    birth_dates = UserProfile.objects.values_list('birthdate', flat=True)
    ages = [(date.today() - birthdate).days // 365 for birthdate in birth_dates]

    age_groups = {
    '18-24': range(18, 25),
    '25-34': range(25, 35),
    '35-44': range(35, 45),
    '45-54': range(45, 55),
    '55+': range(55, 110),
}

    # Count the number of users in each age group
    age_counts = {group: 0 for group in age_groups}
    for age in ages:
        for group, age_range in age_groups.items():
            if age in age_range:
                age_counts[group] += 1
                break

    labels = list(age_counts.keys())
    values = list(age_counts.values())

    plt.figure(figsize=(10, 6))
    plt.bar(labels, values)
    plt.title('Age Group Distribution')
    plt.xlabel('Age Group')
    plt.ylabel('Number of Users')
    plt.tight_layout()

    # Save the chart as a PNG image in memory
    buffer = io.BytesIO()
    plt.savefig(buffer, format='png')
    buffer.seek(0)
    age_group_bar = base64.b64encode(buffer.read()).decode('utf-8')
    plt.close()
    buffer.close()

    #################################### Favourite food by Age Group
    now = datetime.now()
    current_year = now.year
    users = UserProfile.objects.all()
    age_groups = [(current_year - user.birthdate.year) // 10 for user in users]
    age_group_counts = pd.Series(age_groups).value_counts().sort_index()

    # get the most rated food data
    food_ratings_count = Rating.objects.values('food').annotate(count=Count('food')).order_by('-count')

    food_names = [fr['food'] for fr in food_ratings_count]
    food_counts_all = [fr['count'] for fr in food_ratings_count]

    # create dictionary to store food counts for each age group
    food_counts = {}
    for age_group in age_groups:
        food_counts[age_group] = {}
        for food in food_ratings_count:
            ratings = Rating.objects.filter(food=food['food'], user__userprofile__birthdate__year__lte=current_year-age_group*10, user__userprofile__birthdate__year__gt=current_year-(age_group+1)*10)
            food_counts[age_group][food['food']] = ratings.count()

    # create stacked bar chart
    fig, ax = plt.subplots()
    ax.set_xlabel('Number of Ratings')
    ax.set_ylabel('Age Group')
    ax.set_title('Most Rated Foods by Age Group')
    y_pos = np.arange(len(age_groups))

    for i, food in enumerate(food_names):
        counts = [food_counts[age_group].get(food, 0) for age_group in age_groups]
        ax.barh(y_pos, counts, label=food, left=np.sum([food_counts_all[j] if j < i else 0 for j in range(len(food_names))], axis=0))

    ax.set_yticks(y_pos)
    ax.set_yticklabels(age_groups)
    ax.legend(bbox_to_anchor=(1, 1), loc='upper left', borderaxespad=0, fontsize="8")



    # Save the chart as a PNG image in memory
    buffer = io.BytesIO()
    plt.savefig(buffer, format='png')
    buffer.seek(0)
    age_group_food = base64.b64encode(buffer.read()).decode('utf-8')
    plt.close()
    buffer.close()

    return combined_ratings, most_rated_food_graph, favourite_categories_graph, pref_location_graph, gender_graph, age_group_bar, #age_group_food
