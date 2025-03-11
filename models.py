from sqlalchemy import Column, Integer, Float, String, DateTime
from database import Base

class HomepageLoadInformation(Base):
    _tablename_ = 'homepage_load_time'
    id = Column(Integer, primary_key = True, index = True)
    load_time = Column(Float, index = True)
    timestamp = Column(DateTime, index = True)

class RestaurantReviews(Base):
    _tablename_ = 'restaurant_reviews'
    id = Column(Integer, primary_key = True, index = True)
    restaurant_name = Column(String, index = True)
    review_score = Column(Float, index = True)
    start_timestamp = Column(DateTime, index = True) 
    end_timestamp = Column(DateTime, index = True)

class FilterButtonsUsage(Base):
    _tablename_ = 'filter_buttons_usage'
    id = Column(Integer, primary_key = True, index = True)
    filter_name = Column(String, index = True)
    count = Column(Integer, index = True)
    percentage = Column(Float, index = True)

class FoodListing(Base):
    _tablename_ = 'food_listing'
    id = Column(Integer, primary_key = True, index = True)
    category_name = Column(String, index = True)
    count = Column(Integer, index = True)
    percentage = Column(Float, index = True)

    