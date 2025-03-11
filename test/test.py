from firebase_admin import credentials, firestore
from datetime import datetime
from faker import Faker
import firebase_admin
import random


cred = credentials.Certificate("biteback-89c7a-firebase-adminsdk-fbsvc-5ce126e950.json")  
firebase_admin.initialize_app(cred)

db = firestore.client()

fake = Faker()


def generate_test_data():
    for _ in range(10):
        data = {
            "load_time": round(random.uniform(1.0, 5.0), 2),
            "timestamp": datetime.now()
        }
        db.collection("homepage_load_time").add(data)

    for _ in range(10):
        restaurant_names = [fake.company() for _ in range(5)]  
        data = {
            "restaurant_name": random.choice(restaurant_names),  
            "review_score": random.randint(1, 5),  
            "timestamp": datetime.now()
        }
        db.collection("restaurant_reviews").add(data)

    filters = ["Price", "Distance", "Rating", "Cuisine"]
    for _ in range(10):
        data = {
            "filter_name": random.choice(filters),
            "count": 1,  
            "timestamp": datetime.now()
        }
        db.collection("filter_buttons_usage").add(data)

    categories = ["Pizza", "Burgers", "Sushi", "Salads", "Desserts"]
    for _ in range(10):
        data = {
            "category_name": random.choice(categories),
            "count": 1,  
            "timestamp": datetime.now()
        }
        db.collection("food_listing").add(data)

    print("Datos de prueba insertados correctamente en Firestore!")

generate_test_data()
