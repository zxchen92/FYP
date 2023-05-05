import io
import base64
import matplotlib
import matplotlib.pyplot as plt
matplotlib.use('Agg')
from django.db.models import Count
from .models import Rating
from .models import UserProfile
from .models import FoodCategory


def data_insights():
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
    plt.title('Top 10 Most Rated Foods')
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

    #################################

    favourite_category_count = UserProfile.objects.values('foodCategory').annotate(count=Count('foodCategory')).order_by('-count')

    top_categories = [fC['foodCategory'] for fC in favourite_category_count[:10]]
    print("" + str(top_categories))

    category_names = []
    for category_id in top_categories:
        category = FoodCategory.objects.get(id=category_id)
        category_name = category.categoryName
        category_names.append(category_name)




    # Create a bar chart of the top 10 most rated foods
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

    ################################################
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

    ################################################
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

    return most_rated_food_graph, favourite_categories_graph, pref_location_graph, gender_graph
