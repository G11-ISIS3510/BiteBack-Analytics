from sqlalchemy import Column, Integer, Float, String, DateTime, UniqueConstraint
from database import Base
from datetime import datetime
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
    
class ClickInteraction(Base):
    __tablename__ = 'click_interaction'
    id = Column(String, primary_key=True, index=True)
    category_product_name = Column(String, index=True)
    week = Column(Integer, index=True)
    year = Column(Integer, index=True)
    click_count = Column(Integer, index=True)
    
class PopularityIndex(Base):
    __tablename__ = 'popularity_index'
    id = Column(String, primary_key=True, index=True)
    category = Column(String, index=True)
    popularity_score = Column(Float, index=True)

class UserDevices(Base):
    __tablename__ = 'user_devices'
    device_model = Column(String, primary_key=True, index=True)
    user_count = Column(Integer, index=True)

class TopProductsByWeek(Base):
    __tablename__ = 'top_products_by_week'
    id = Column(String, primary_key=True, index=True)
    product_id = Column(String, index=True)
    name = Column(String, index=True)
    quantity = Column(Integer)
    week = Column(Integer)
    year = Column(Integer)

class CheckoutSessionStats(Base):
    __tablename__ = 'checkout_session_stats'
    id = Column(String, primary_key=True, index=True)
    week = Column(Integer)
    year = Column(Integer)
    avg_duration = Column(Float)

class CheckoutTimeAnalytics(Base):
    __tablename__ = "checkout_time_analytics"

    id = Column(Integer, primary_key=True, index=True)
    average_minutes = Column(Float)
    day_of_week = Column(String, nullable=True)  
    hour = Column(Integer, nullable=True)        
    timestamp = Column(DateTime, default=datetime.utcnow)


class CheckoutSummaryAnalytics(Base):
    __tablename__ = "checkout_summary_analytics"

    id = Column(Integer, primary_key=True, index=True)
    day_of_week = Column(String, nullable=True)  # None para 'forgotten'
    sales_count = Column(Integer, nullable=False)
    type = Column(String, nullable=False)  # 'forgotten' o 'completed'
    timestamp = Column(DateTime, default=datetime.utcnow)

    __table_args__ = (
        UniqueConstraint('day_of_week', 'type', name='unique_day_type'),
    )
    
class CartpageLoadInformation(Base):
    __tablename__ = 'cartpage_load_time'
    id = Column(String, primary_key=True, index=True)
    load_time = Column(Float, index=True)
    timestamp = Column(DateTime, index=True)


class ProductPairAnalytics(Base):
    __tablename__ = 'product_pair_analytics'
    id = Column(String, primary_key=True, index=True)
    product_a = Column(String, index=True)
    product_b = Column(String, index=True)
    name_a = Column(String, index=True)
    name_b = Column(String, index=True)
    count = Column(Integer, index=True)


class UserAndroidVersion(Base):
    __tablename__ = 'user_android_versions'
    android_version = Column(String, primary_key=True, index=True)
    user_count = Column(Integer, index=True)


class UserAndroidSDK(Base):
    __tablename__ = 'user_android_sdks'
    android_sdk = Column(String, primary_key=True, index=True)
    user_count = Column(Integer, index=True)

class Product(Base):
    __tablename__ = 'products'
    product_id = Column(String, primary_key=True, index=True)
    category = Column(String, index=True)
