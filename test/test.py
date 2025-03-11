from firebase_admin import credentials, firestore
from datetime import datetime
from faker import Faker
import firebase_admin
import random


cred = credentials.Certificate("biteback-89c7a-firebase-adminsdk-fbsvc-5ce126e950.json")  
firebase_admin.initialize_app(cred)

db = firestore.client()

# To create test data
fake = Faker()


def generate_test_data():

    # Populating the homepage_load_time table
    for _ in range(10):
        data = {
            "load_time": round(random.uniform(1.0, 5.0), 2),
            "timestamp": datetime.now()
        }
        db.collection("homepage_load_time").add(data)

    # Populating the restaurant_reviews table
    restaurant_names = [fake.company() for _ in range(5)]  
    for _ in range(10):
        data = {
            "restaurant_name": random.choice(restaurant_names),  
            "review_score": random.randint(1, 5),  
            "timestamp": datetime.now()
        }
        db.collection("restaurant_reviews").add(data)

    # Populating the filter_buttons_usage table
    filters = ["Price", "Distance", "Rating", "Cuisine"]
    for _ in range(10):
        data = {
            "filter_name": random.choice(filters),
            "count": 1,  
            "timestamp": datetime.now()
        }
        db.collection("filter_buttons_usage").add(data)

    # Populating the food_listing table
    categories = ["Pizza", "Burgers", "Sushi", "Salads", "Desserts"]
    for _ in range(10):
        data = {
            "category_name": random.choice(categories),
            "count": 1,  
            "timestamp": datetime.now()
        }
        db.collection("food_listing").add(data)

    print("Test data successfully inserted in Firestore!")

generate_test_data()
