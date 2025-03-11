from sqlalchemy import Column, Integer, Float, String, DateTime
from database import Base

class HomepageLoadInformation(Base):
    __tablename__ = 'homepage_load_time'
    id = Column(Integer, primary_key = True, index = True)
    load_time = Column(Float, index = True)
    timestamp = Column(DateTime, index = True)

class RestaurantReviews(Base):
    __tablename__ = 'restaurant_reviews'
    id = Column(Integer, primary_key = True, index = True, autoincrement = True)
    restaurant_name = Column(String, index = True)
    review_score = Column(Float, index = True)
    week = Column(Integer, index = True) 
    year = Column(Integer, index = True)

class FilterButtonsUsage(Base):
    __tablename__ = 'filter_buttons_usage'
    id = Column(Integer, primary_key = True, index = True, autoincrement = True)
    filter_name = Column(String, index = True)
    count = Column(Integer, index = True)
    percentage = Column(Float, index = True)

class FoodListing(Base):
    __tablename__ = 'food_listing'
    id = Column(Integer, primary_key = True, index = True, autoincrement = True)
    category_name = Column(String, index = True)
    count = Column(Integer, index = True)
    percentage = Column(Float, index = True)

    