import io
import base64
import matplotlib
import matplotlib.pyplot as plt
matplotlib.use('Agg')
from django.db.models import Count
from .models import Rating

def data_insights():
    # Get the count of ratings for each food
    food_rating_counts = Rating.objects.values('food').annotate(count=Count('food')).order_by('-count')

    # Get the names of the top 10 most rated foods
    top_foods = [f['food'] for f in food_rating_counts[:10]]
    print(""+ str(top_foods))
   
    # Create a bar chart of the top 10 most rated foods
    counts = [f['count'] for f in food_rating_counts[:10]]
    plt.bar(top_foods, counts)
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

    return most_rated_food_graph
