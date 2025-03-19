from sqlalchemy import Column, Integer, Float, String, DateTime
from database import Base

class HomepageLoadInformation(Base):
    __tablename__ = 'homepage_load_time'
    id = Column(String, primary_key = True, index = True)
    load_time = Column(Float, index = True)
    timestamp = Column(DateTime, index = True)

class RestaurantReviews(Base):
    __tablename__ = 'restaurant_reviews'
    id = Column(String, primary_key = True, index = True)
    restaurant_name = Column(String, index = True)
    review_score = Column(Float, index = True)
    week = Column(Integer, index = True) 
    year = Column(Integer, index = True)

class FilterButtonsUsage(Base):
    __tablename__ = 'filter_buttons_usage'
    id = Column(String, primary_key = True, index = True)
    filter_name = Column(String, index = True)
    count = Column(Integer, index = True)
    percentage = Column(Float, index = True)

class FoodListing(Base):
    __tablename__ = 'food_listing'
    id = Column(String, primary_key = True, index = True)
    category_name = Column(String, index = True)
    count = Column(Integer, index = True)
    percentage = Column(Float, index = True)

class SearchesAnalytics(Base):
    __tablename__ = 'searches_analytics'
    id = Column(String, primary_key=True, index=True)
    search_term = Column(String, index=True)
    count = Column(Integer, index=True)
    normalized_term = Column(String, index=True)
    percentage = Column(Float, index=True)