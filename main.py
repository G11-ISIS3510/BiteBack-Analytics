from firebase_admin import credentials, firestore
from database import engine, SessionLocal
from fastapi import FastAPI, Depends
import firebase_admin as fire_admin
from sqlalchemy.orm import Session
from typing import Annotated
import pandas as pd
import models


creds = credentials.Certificate('biteback-89c7a-firebase-adminsdk-fbsvc-5ce126e950.json')
app = fire_admin.initialize_app(creds)
firestore_DB = firestore.client()

app = FastAPI()
models.Base.metadata.create_all(bind = engine)


def get_DB():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


db_dependency = Annotated[Session, Depends(get_DB)]


@app.get('/')
async def root():
    return {'message' : 'BiteBack Analytics API is working'}


@app.get('/homepage-load-time')
async def setup(db: db_dependency):
    try:
        # Retrieving information from firestore database 
        docs = firestore_DB.collection('homepage_load_time').stream()

        # Turning documents into a pandas dataframe
        docs_array = []
        for doc in docs:
            data = doc.to_dict()
            data['id'] = doc.id
            docs_array.append(data)
        docs_df = pd.DataFrame(docs_array)

        if docs_df.empty:
            return {'message' : "There is no data about the homepage load time"}

        # Iterate over the dataframe and update analytics database
        for _, row in docs_df.iterrows():
            existing_entry = db.query(models.HomepageLoadInformation).filter(
                models.HomepageLoadInformation.id == row['id']
            ).first()

            # If the entry doesnt exist in the analytics database, insert it
            if not existing_entry:
                new_entry = models.HomepageLoadInformation(
                    id = row['id'], 
                    load_time = row['load_time'], 
                    timestamp = row['timestamp']
                )
                db.add(new_entry)

        # Save the analytics database
        db.commit()
        return {'message' : 'Analytics database updated [homepage_load_time]'}
    
    except Exception as e:
        # Rollback if any error happens
        db.rollback()
        return {'error' : str(e)}


@app.get('/most-liked-restaurants')
async def setup(db: db_dependency):
    try:
        # Retrieving information from firestore database
        docs = firestore_DB.collection('restaurant_reviews').stream()

        # Turning documents into a pandas dataframe
        docs_array = []
        for doc in docs:
            data = doc.to_dict()
            data['id'] = doc.id
            docs_array.append(data)
        docs_df = pd.DataFrame(docs_array)

        if docs_df.empty:
            return {'message' : 'There is no data about the restaurants reviews'}
        
        # Transforming necessary data
        docs_df['week'] = docs_df['timestamp'].dt.isocalendar().week
        docs_df['year'] = docs_df['timestamp'].dt.isocalendar().year

        # Group data by restaurant name, year and week. Merge review score using the mean
        df_grouped = docs_df.groupby(['restaurant_name', 'year', 'week']).agg(review_score = ('review_score', 'mean'), id = ('id', 'first')).reset_index()
        df_grouped = df_grouped.sort_values(by = ['year', 'week', 'restaurant_name'])

        # Iterate over the dataframe and update analytics database
        for _, row in df_grouped.iterrows():
            existing_entry = db.query(models.RestaurantReviews).filter(
                models.RestaurantReviews.restaurant_name == row['restaurant_name'],
                models.RestaurantReviews.week == row['week'],
                models.RestaurantReviews.year == row['year']
            ).first()
            
            # If the entry doesnt exist in the analytics database, insert it
            if not existing_entry:
                new_entry = models.RestaurantReviews(
                    id = row['id'],
                    restaurant_name = row['restaurant_name'],
                    week = row['week'],
                    year = row['year'],
                    review_score = row['review_score']
                )
                db.add(new_entry)
                db.commit()

            else:
                # Update review score
                existing_entry.review_score = row['review_score']
                db.commit()
            
        # Save the analytics database
        db.commit()
        return {'message' : 'Analytics database updated [restaurant_reviews]'}
    
    except Exception as e:
        # Rollback if any error happens
        db.rollback()
        return {'error' : str(e)}


@app.get('/most-used-filters')
async def setup(db: db_dependency):
    try:
        # Retrieving information from firestore database
        docs = firestore_DB.collection('filter_buttons_usage').stream()

        # Turning documents into a pandas dataframe
        docs_array = []
        for doc in docs:
            data = doc.to_dict()
            data['id'] = doc.id
            docs_array.append(data)
        docs_df = pd.DataFrame(docs_array)

        if docs_df.empty:
            return {'message' : 'There is no data about the filters usage'}
        
        # Group data by filter name. Merge count using sum
        df_grouped = docs_df.groupby(['filter_name']).agg(count = ('count', 'sum'), id = ('id', 'first')).reset_index()
        df_grouped = df_grouped.sort_values(by = ['filter_name'])

        total_count = df_grouped['count'].sum()

        # Iterate over the dataframe and update analytics database
        for _, row in df_grouped.iterrows():
            existing_entry = db.query(models.FilterButtonsUsage).filter(
                models.FilterButtonsUsage.filter_name == row['filter_name'],
            ).first()
            
            # If the entry doesnt exist in the analytics database, insert it
            if not existing_entry:
                new_entry = models.FilterButtonsUsage(
                    id = row['id'],
                    filter_name = row['filter_name'],
                    count = row['count'],
                    percentage = round(float(row['count'] * 100 / total_count), 2)
                )
                db.add(new_entry)
                db.commit()
            else:
                # Update filter count and percentage
                existing_entry.count = row['count']
                existing_entry.percentage = round(float(row['count'] * 100 / total_count), 2)
                db.commit()
            
        # Save the analytics database
        db.commit()
        return {'message' : 'Analytics database updated [filter_buttons_usage]'}
    
    except Exception as e:
        # Rollback if any error happens
        db.rollback()
        return {'error' : str(e)}


@app.get('/categories-frequencies')
async def setup(db: db_dependency):
    try:
        # Retrieving information from firestore database
        docs = firestore_DB.collection('food_listing').stream()

        # Turning documents into a pandas dataframe
        docs_array = []
        for doc in docs:
            data = doc.to_dict()
            data['id'] = doc.id
            docs_array.append(data)
        docs_df = pd.DataFrame(docs_array)

        if docs_df.empty:
            return {'message' : 'There is no data about the food categories'}
        
        # Group data by filter name. Merge count using sum
        df_grouped = docs_df.groupby(['category_name']).agg(count = ('count', 'sum'), id = ('id', 'first')).reset_index()
        df_grouped = df_grouped.sort_values(by = ['category_name'])

        total_count = df_grouped['count'].sum()

        # Iterate over the dataframe and update analytics database
        for _, row in df_grouped.iterrows():
            existing_entry = db.query(models.FoodListing).filter(
                models.FoodListing.category_name == row['category_name'],
            ).first()
            
            # If the entry doesnt exist in the analytics database, insert it
            if not existing_entry:
                new_entry = models.FoodListing(
                    id = row['id'],
                    category_name = row['category_name'],
                    count = row['count'],
                    percentage =  round(float(row['count'] * 100 / total_count), 2)
                )
                db.add(new_entry)
                db.commit()

            else:
                # Update filter count and percentage
                existing_entry.count = row['count']
                existing_entry.percentage =  round(float(row['count'] * 100 / total_count), 2)
                db.commit()

        # Save the analytics database
        db.commit()
        return {'message' : 'Analytics database updated [food_listing]'}
    
    except Exception as e:
        # Rollback if any error happens
        db.rollback()
        return {'error' : str(e)}


@app.get('/clean-homepage-load-time')
def setup(db: Session = Depends(get_DB)):
    try:
        # Delete all information on the table
        db.query(models.HomepageLoadInformation).delete()
        db.commit()
        return {'message': 'homepage_load_time cleaned'}
    
    except Exception as e:
        # Rollback if any error happens
        db.rollback()  
        return {"error": str(e)}


@app.get('/clean-most-liked-restaurants')
def setup(db: Session = Depends(get_DB)):
    try:
        # Delete all information on the table
        db.query(models.RestaurantReviews).delete()
        db.commit()
        return {'message': 'restaurant_reviews cleaned'}
    
    except Exception as e:
        # Rollback if any error happens
        db.rollback()  
        return {"error": str(e)}


@app.get('/clean-most-used-filters')
def setup(db: Session = Depends(get_DB)):
    try:
        # Delete all information on the table
        db.query(models.FilterButtonsUsage).delete()
        db.commit()
        return {'message': 'filter_buttons_usage cleaned'}
    
    except Exception as e:
        # Rollback if any error happens
        db.rollback()  
        return {"error": str(e)}


@app.get('/clean-categories-frequencies')
def setup(db: Session = Depends(get_DB)):
    try:
        # Delete all information on the table
        db.query(models.FoodListing).delete()
        db.commit()
        return {'message': 'food_listing cleaned'}
    
    except Exception as e:
        # Rollback if any error happens
        db.rollback()  
        return {"error": str(e)}
