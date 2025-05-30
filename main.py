from firebase_admin import credentials, firestore, initialize_app
from database import engine, SessionLocal
from fastapi import FastAPI, Depends
import firebase_admin as fire_admin
from sqlalchemy.orm import Session
from typing import Annotated
import pandas as pd
import models
import re
from collections import Counter
from difflib import get_close_matches
import nltk
from nltk.stem import WordNetLemmatizer
from datetime import datetime

nltk.download('wordnet')
nltk.download('omw-1.4')


"""from database import engine
from models import Base
Base.metadata.drop_all(bind=engine)
Base.metadata.create_all(bind=engine)"""


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

lemmatizer = WordNetLemmatizer()


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

def normalize_text(text):
    text = text.lower()
    text = re.sub(r'[^a-zA-Z0-9 ]', '', text)  # Remove special characters
    text = ' '.join([lemmatizer.lemmatize(word) for word in text.split()])  # English lemmatization
    return text.strip()

@app.get('/search-analytics')
async def setup(db: db_dependency):
    try:
        # Retrieving information from firestore database
        docs = firestore_DB.collection('searches').stream()

        # Turning documents into a pandas dataframe
        docs_array = []
        for doc in docs:
            data = doc.to_dict()
            data['id'] = doc.id
            docs_array.append(data)
        docs_df = pd.DataFrame(docs_array)

        if docs_df.empty:
            return {'message': 'There is no data about searches'}
        
        # Normalize search terms
        docs_df['normalized_term'] = docs_df['text'].apply(normalize_text)
        
        # Count occurrences of each term
        term_counts = Counter(docs_df['normalized_term'])
        total_count = sum(term_counts.values())
        
        # Group close matches
        unique_terms = list(term_counts.keys())
        grouped_terms = {}

        for term in unique_terms:
            match = get_close_matches(term, grouped_terms.keys(), n=1, cutoff=0.8)
            if match:
                grouped_terms[match[0]] += term_counts[term]
            else:
                grouped_terms[term] = term_counts[term]
        
        # Convert to DataFrame
        analytics_df = pd.DataFrame(grouped_terms.items(), columns=['normalized_term', 'count'])
        analytics_df['percentage'] = round((analytics_df['count'] / total_count) * 100, 2)
        analytics_df['id'] = analytics_df['normalized_term']

        # Iterate over the dataframe and update analytics database
        for _, row in analytics_df.iterrows():
            existing_entry = db.query(models.SearchesAnalytics).filter(
                models.SearchesAnalytics.normalized_term == row['normalized_term']
            ).first()
            
            # If the entry doesnt exist in the analytics database, insert it
            if not existing_entry:
                new_entry = models.SearchesAnalytics(
                    id=row['id'],
                    search_term=row['normalized_term'],
                    count=row['count'],
                    normalized_term=row['normalized_term'],
                    percentage=row['percentage']
                )
                db.add(new_entry)
            else:
                # Update search count and percentage
                existing_entry.count = row['count']
                existing_entry.percentage = row['percentage']
                db.commit()
        
        db.commit()
        return {'message': 'Analytics database updated [searches_analytics]'}
    
    except Exception as e:
        db.rollback()
        return {'error': str(e)}


@app.get('/click-interactions')
async def process_clicks(db: db_dependency):
    try:
        # Retrieving click interaction data from Firestore
        docs = firestore_DB.collection('click_interaction').stream()

        # Turning documents into a pandas dataframe
        docs_array = []
        for doc in docs:
            data = doc.to_dict()
            data['id'] = doc.id
            docs_array.append(data)
        docs_df = pd.DataFrame(docs_array)

        if docs_df.empty:
            return {'message': 'There is no data about click interactions'}
        
        # Ensure timestamp column exists and convert to datetime
        if 'timestamp' in docs_df.columns:
            docs_df['timestamp'] = pd.to_datetime(docs_df['timestamp'], errors='coerce')
            docs_df = docs_df.dropna(subset=['timestamp'])  # Remove rows where timestamp is NaT
        else:
            return {'message': 'Missing timestamp data'}
        
        # Extract week and year from timestamp
        docs_df['week'] = docs_df['timestamp'].dt.isocalendar().week
        docs_df['year'] = docs_df['timestamp'].dt.isocalendar().year
        
        # Group by category, week, and year, counting interactions
        df_grouped = docs_df.groupby(['category-product-name', 'year', 'week']).agg(
            click_count=('id', 'count')
        ).reset_index()
        df_grouped = df_grouped.sort_values(by=['year', 'week', 'category-product-name'])
        
        # Iterate over the dataframe and update the database
        for _, row in df_grouped.iterrows():
            existing_entry = db.query(models.ClickInteraction).filter(
                models.ClickInteraction.category_product_name == row['category-product-name'],
                models.ClickInteraction.week == row['week'],
                models.ClickInteraction.year == row['year']
            ).first()
            
            # If the entry does not exist, insert it
            if not existing_entry:
                new_entry = models.ClickInteraction(
                    id=f"{row['category-product-name']}_{row['year']}_{row['week']}",
                    category_product_name=row['category-product-name'],
                    week=row['week'],
                    year=row['year'],
                    click_count=row['click_count']
                )
                db.add(new_entry)
            else:
                # Update existing entry if necessary
                existing_entry.click_count = row['click_count']
                db.commit()
        
        db.commit()
        return {'message': 'Analytics database updated [click_interaction]'}
    
    except Exception as e:
        db.rollback()
        return {'error': str(e)}
    
@app.get('/calculate-popularity')
async def calculate_popularity(db: db_dependency):
    try:
        # Fetching data from tables
        searches = pd.read_sql(db.query(models.SearchesAnalytics).statement, db.bind)
        filters = pd.read_sql(db.query(models.FilterButtonsUsage).statement, db.bind)
        clicks = pd.read_sql(db.query(models.ClickInteraction).statement, db.bind)

        # Ensure category fields are strings
        searches["normalized_term"] = searches["normalized_term"].astype(str)
        filters["filter_name"] = filters["filter_name"].astype(str)
        clicks["category_product_name"] = clicks["category_product_name"].astype(str)

        # Normalizing metrics
        def min_max_normalize(series):
            return (series - series.min()) / (series.max() - series.min()) if series.max() != series.min() else series

        searches["S_norm"] = min_max_normalize(searches["count"])
        filters["F_norm"] = min_max_normalize(filters["count"])
        clicks["C_norm"] = min_max_normalize(clicks["click_count"])

        # Merging data
        popularity_df = searches.merge(clicks, left_on="normalized_term", right_on="category_product_name", how="outer").fillna(0)
        popularity_df = popularity_df.merge(filters, left_on="normalized_term", right_on="filter_name", how="outer").fillna(0)

        # Calculating popularity score
        w1, w2, w3 = 0.2, 0.3, 0.5
        popularity_df["popularity_score"] = (w1 * popularity_df["S_norm"]) + (w2 * popularity_df["F_norm"]) + (w3 * popularity_df["C_norm"])
        popularity_df["popularity_score"] *= 100  # Scaling to 0-100

        # Storing results in the database
        for _, row in popularity_df.iterrows():
            category_value = row['normalized_term'] if row['normalized_term'] != '0' else None
            if category_value:
                entry_id = f"{category_value}_{datetime.utcnow().strftime('%Y%m%d%H%M%S')}"
                existing_entry = db.query(models.PopularityIndex).filter(
                    models.PopularityIndex.category == category_value
                ).first()
                
                if not existing_entry:
                    new_entry = models.PopularityIndex(
                        id=entry_id,
                        category=category_value,
                        popularity_score=row['popularity_score']
                    )
                    db.add(new_entry)
                else:
                    existing_entry.popularity_score = row['popularity_score']
                    db.commit()

        db.commit()
        return {"message": "Popularity index calculated and stored successfully"}
    
    except Exception as e:
        db.rollback()
        return {"error": str(e)}
    
@app.get('/users-by-device')
async def users_by_device(db: db_dependency):
    try:
        # Traer todos los documentos de la colección 'users'
        docs = firestore_DB.collection('users').stream()

        devices = {}
        for doc in docs:
            data = doc.to_dict()
            device_model = data.get('device_model', 'Unknown')

            # Contar ocurrencias por modelo
            if device_model in devices:
                devices[device_model] += 1
            else:
                devices[device_model] = 1

        # Guardar en PostgreSQL
        for device, count in devices.items():
            existing_entry = db.query(models.UserDevices).filter(
                models.UserDevices.device_model == device
            ).first()

            if not existing_entry:
                new_entry = models.UserDevices(
                    device_model=device,
                    user_count=count
                )
                db.add(new_entry)
            else:
                existing_entry.user_count = count

        db.commit()
        return {'message': 'User devices aggregated and stored successfully'}

    except Exception as e:
        db.rollback()
        return {'error': str(e)}

@app.get('/clean-users-by-device')
def setup(db: Session = Depends(get_DB)):
    try:
        # Delete all information on the table
        db.query(models.UserDevices).delete()
        db.commit()
        return {'message': 'UserDevices cleaned'}
    
    except Exception as e:
        # Rollback if any error happens
        db.rollback()  
        return {"error": str(e)} 

@app.get("/checkout-session-analytics")
async def process_checkout_sessions(db: db_dependency):
    print("🔍 Iniciando procesamiento de sesiones de checkout...")

    records = []
    durations = []
    processed_docs = 0

    user_docs = firestore_DB.collection('checkout_sessions').list_documents()
    uids = [doc.id for doc in user_docs]
    print(f"🧾 UIDs encontrados: {uids}")

    for uid in uids:
        entry_docs = firestore_DB.collection(f'checkout_sessions/{uid}/entries').stream()
        for entry_doc in entry_docs:
            data = entry_doc.to_dict()
            print(f"📦 Procesando entrada: {entry_doc.id} de usuario {uid}")
            print("🧾 Contenido:", data)

            processed_docs += 1

            if 'completed_at' in data and 'duration_ms' in data and 'items' in data:
                ts = pd.to_datetime(data['completed_at'].isoformat())
                week = ts.isocalendar().week
                year = ts.isocalendar().year

                durations.append({
                    'id': f"{uid}_{year}_{week}",
                    'week': week,
                    'year': year,
                    'avg_duration': data['duration_ms']
                })

                for item in data['items']:
                    records.append({
                        'id': f"{uid}_{item['product_id']}_{year}_{week}",
                        'product_id': item['product_id'],
                        'name': item['name'],
                        'quantity': item['quantity'],
                        'week': week,
                        'year': year
                    })

    print(f"📊 Total documentos procesados: {processed_docs}")

    product_df = pd.DataFrame(records)
    duration_df = pd.DataFrame(durations)

    if not product_df.empty:
        grouped = product_df.groupby(['product_id', 'name', 'week', 'year']).agg(
            quantity=('quantity', 'sum')).reset_index()
        grouped['id'] = grouped.apply(lambda r: f"{r['product_id']}_{r['year']}_{r['week']}", axis=1)

        for _, row in grouped.iterrows():
            existing = db.query(models.TopProductsByWeek).filter(models.TopProductsByWeek.id == row['id']).first()
            if not existing:
                entry = models.TopProductsByWeek(**row)
                db.add(entry)
            else:
                existing.quantity = row['quantity']
        db.commit()
    else:
        print("⚠️ No se encontraron productos para procesar")

    if not duration_df.empty:
        grouped_dur = duration_df.groupby(['week', 'year']).agg(
            avg_duration=('avg_duration', 'mean')).reset_index()
        grouped_dur['id'] = grouped_dur.apply(lambda r: f"{r['year']}_{r['week']}", axis=1)

        for _, row in grouped_dur.iterrows():
            existing = db.query(models.CheckoutSessionStats).filter(models.CheckoutSessionStats.id == row['id']).first()
            if not existing:
                entry = models.CheckoutSessionStats(**row)
                db.add(entry)
            else:
                existing.avg_duration = row['avg_duration']
        db.commit()
    else:
        print("⚠️ No se encontraron duraciones para procesar")

    return {'message': 'Checkout session analytics processed ✅'}



@app.get("/avg-checkout-time")
async def checkout_time_analysis(db: db_dependency):
    try:
        # 1. Obtener documentos de Firestore
        docs = firestore_DB.collection('purchases').stream()
        docs_array = []
        for doc in docs:
           
            data = doc.to_dict()
            data['id'] = doc.id
            docs_array.append(data)

        df = pd.DataFrame(docs_array)
   
        if df.empty:
            return {'message': 'No checkout session data available'}

        # 2. Filtrar compras completadas
        df_completed = df[df['elapsedTimeMillis'].notnull()].copy()
        if df_completed.empty:
            return {'message': 'No completed purchases found'}

        # 3. Convertir tiempos
        df_completed['elapsed_minutes'] = df_completed['elapsedTimeMillis'] / 60000

        # 4. Calcular promedios
        general_avg = round(df_completed['elapsed_minutes'].mean(), 2)

        # Promedio por día de la semana
        df_completed['day_of_week'] = df_completed['day_of_week'].astype(str)
        avg_by_day = df_completed.groupby('day_of_week')['elapsed_minutes'].mean().round(2).to_dict()

        # Promedio por hora (extraído de 'time' string)
        df_completed['hour'] = pd.to_datetime(df_completed['time'], format="%H:%M:%S").dt.hour
        avg_by_hour = df_completed.groupby('hour')['elapsed_minutes'].mean().round(2).to_dict()
        

        print("Promedio general:", general_avg)
        print("Por día:", avg_by_day)
        print("Por hora:", avg_by_hour)


        # 5. (Opcional) Guardar análisis en la base de datos
        # Guardar promedio general
      
        db.add(models.CheckoutTimeAnalytics(
            average_minutes=float(general_avg),  # o general_avg.item() si es np.float64
            day_of_week=None,
            hour=None
        ))

        # Guardar por día
        for day, avg in avg_by_day.items():
            db.add(models.CheckoutTimeAnalytics(
                average_minutes=float(avg),
                day_of_week=day,
                hour=None
            ))

        # Guardar por hora
        for hour, avg in avg_by_hour.items():
            db.add(models.CheckoutTimeAnalytics(
                average_minutes=float(avg),
                day_of_week=None,
                hour=int(hour)
            ))

        try:
            db.commit()
            print("Datos guardados correctamente.")
        except Exception as e:
            db.rollback()
            print("Error al guardar:", e)

        # 6. Devolver respuesta
        return {
            "general_average_minutes": general_avg,
            "average_by_day_of_week": avg_by_day,
            "average_by_hour": avg_by_hour
        }

    except Exception as e:
        db.rollback()
        return {"error": str(e)}


def upsert_checkout_summary(db: Session, day_of_week: str, type_: str, count: int):
    existing = db.query(models.CheckoutSummaryAnalytics).filter_by(
        day_of_week=day_of_week,
        type=type_
    ).first()

    if existing:
        existing.sales_count = count
        existing.timestamp = datetime.utcnow()
    else:
        db.add(models.CheckoutSummaryAnalytics(
            day_of_week=day_of_week,
            sales_count=count,
            type=type_
        ))


@app.get("/checkout-summary")
async def checkout_summary(db: db_dependency):
    try:
        # 1. Leer Firestore
        docs = firestore_DB.collection('purchases').stream()
        docs_array = [doc.to_dict() for doc in docs]

        df = pd.DataFrame(docs_array)

        if df.empty:
            return {"message": "No purchase data available."}

        # 2. Total olvidos de pago
        forgotten_count = df[df['elapsedTimeMillis'].isnull()].shape[0]

        # Guardar olvidos (day_of_week=None, type='forgotten')
        upsert_checkout_summary(db, None, "forgotten", forgotten_count)


        # 3. Ventas completadas
        df_completed = df[df['elapsedTimeMillis'].notnull()].copy()

        sales_by_day = {}

        if not df_completed.empty:
            # Normalizar columna
            df_completed['day_of_week'] = df_completed['day_of_week'].astype(str).str.strip().str.capitalize()

            # Agrupar por día
            grouped = df_completed.groupby('day_of_week').size().to_dict()
            sales_by_day = dict(sorted(grouped.items(), key=lambda x: x[1], reverse=True))

            # Guardar cada día como registro en la BD
            for day, count in sales_by_day.items():
                upsert_checkout_summary(db, day, "completed", int(count))

        # Commit final
        try:
            db.commit()
        except Exception as e:
            db.rollback()
            print("Error al guardar en PostgreSQL:", e)

        return {
            "forgotten_checkouts": forgotten_count,
            "sales_by_day": sales_by_day
        }

    except Exception as e:
        db.rollback()
        return {"error": str(e)}

# NUEVO ENDPOINT: Tiempo de carga CartScreen
@app.get('/cartpage-load-time')
async def load_cartpage_times(db: db_dependency):
    try:
        docs = firestore_DB.collection('cartpage_load_time').stream()
        docs_array = []
        for doc in docs:
            data = doc.to_dict()
            data['id'] = doc.id
            docs_array.append(data)
        df = pd.DataFrame(docs_array)

        if df.empty:
            return {'message': "No data found in cartpage_load_time"}

        for _, row in df.iterrows():
            exists = db.query(models.CartpageLoadInformation).filter_by(id=row['id']).first()
            if not exists:
                db.add(models.CartpageLoadInformation(
                    id=row['id'],
                    load_time=row['load_time'],
                    timestamp=row['timestamp']
                ))
        db.commit()
        return {'message': 'Analytics updated [cartpage_load_time]'}

    except Exception as e:
        db.rollback()
        return {'error': str(e)}

# NUEVO ENDPOINT: Pares de productos más comprados juntos
@app.get("/most-common-product-pairs")
async def most_common_product_pairs(db: db_dependency):
    try:
        user_docs = firestore_DB.collection('checkout_sessions').list_documents()
        uids = [doc.id for doc in user_docs]
        pairs = {}

        for uid in uids:
            entries = firestore_DB.collection(f'checkout_sessions/{uid}/entries').stream()
            for entry in entries:
                data = entry.to_dict()
                if 'items' in data:
                    items = sorted(data['items'], key=lambda x: x['product_id'])
                    for i in range(len(items)):
                        for j in range(i + 1, len(items)):
                            a = items[i]
                            b = items[j]
                            pair_id = f"{a['product_id']}_{b['product_id']}"
                            if pair_id not in pairs:
                                pairs[pair_id] = {
                                    "id": pair_id,  # ✅ Campo requerido por la tabla
                                    "product_a": a['product_id'],
                                    "product_b": b['product_id'],
                                    "name_a": a.get('name', 'Producto A'),
                                    "name_b": b.get('name', 'Producto B'),
                                    "count": 1
                                }
                            else:
                                pairs[pair_id]["count"] += 1

        for pair_id, entry in pairs.items():
            existing = db.query(models.ProductPairAnalytics).filter_by(id=pair_id).first()
            if existing:
                existing.count = entry["count"]
            else:
                db.add(models.ProductPairAnalytics(**entry))

        db.commit()
        return {'message': 'Product pairs saved to database'}

    except Exception as e:
        db.rollback()
        return {'error': str(e)}


# NUEVO ENDPOINT: Usuarios por versión de Android
@app.get('/users-by-android-version')
async def users_by_android_version(db: db_dependency):
    try:
        docs = firestore_DB.collection('users').stream()
        versions = {}

        for doc in docs:
            data = doc.to_dict()
            version = data.get('android_version', 'Unknown').strip()
            if not version:
                version = "Unknown"
            versions[version] = versions.get(version, 0) + 1

        for version, count in versions.items():
            existing = db.query(models.UserAndroidVersion).filter_by(android_version=version).first()
            if existing:
                existing.user_count = count
            else:
                db.add(models.UserAndroidVersion(
                    android_version=version,
                    user_count=count
                ))

        db.commit()
        return {'message': 'User Android versions aggregated and stored successfully'}

    except Exception as e:
        db.rollback()
        return {'error': str(e)}

# NUEVO ENDPOINT: Usuarios por SDK de Android
@app.get('/users-by-android-sdk')
async def users_by_android_sdk(db: db_dependency):
    try:
        docs = firestore_DB.collection('users').stream()
        sdk_levels = {}

        for doc in docs:
            data = doc.to_dict()
            sdk = data.get('android_sdk', 'Unknown')
            sdk = str(sdk).strip() if sdk is not None else "Unknown"
            if not sdk or sdk == "-1":
                sdk = "Unknown"
            sdk_levels[sdk] = sdk_levels.get(sdk, 0) + 1

        for sdk, count in sdk_levels.items():
            existing = db.query(models.UserAndroidSDK).filter_by(android_sdk=sdk).first()
            if existing:
                existing.user_count = count
            else:
                db.add(models.UserAndroidSDK(
                    android_sdk=sdk,
                    user_count=count
                ))

        db.commit()
        return {'message': 'User Android SDKs aggregated and stored successfully'}

    except Exception as e:
        db.rollback()
        return {'error': str(e)}

# ENDPOINTS DE LIMPIEZA
@app.get('/clean-cartpage-load-time')
def clean_cartpage_load_time(db: Session = Depends(get_DB)):
    try:
        db.query(models.CartpageLoadInformation).delete()
        db.commit()
        return {'message': 'cartpage_load_time cleaned'}
    except Exception as e:
        db.rollback()
        return {"error": str(e)}

@app.get('/clean-product-pairs')
def clean_product_pairs(db: Session = Depends(get_DB)):
    try:
        db.query(models.ProductPairAnalytics).delete()
        db.commit()
        return {'message': 'product_pair_analytics cleaned'}
    except Exception as e:
        db.rollback()
        return {"error": str(e)}

@app.get('/clean-user-android-versions')
def clean_user_android_versions(db: Session = Depends(get_DB)):
    try:
        db.query(models.UserAndroidVersion).delete()
        db.commit()
        return {'message': 'user_android_versions cleaned'}
    except Exception as e:
        db.rollback()
        return {"error": str(e)}

@app.get('/clean-user-android-sdks')
def clean_user_android_sdks(db: Session = Depends(get_DB)):
    try:
        db.query(models.UserAndroidSDK).delete()
        db.commit()
        return {'message': 'user_android_sdks cleaned'}
    except Exception as e:
        db.rollback()
        return {"error": str(e)}



    
@app.get('/clean-checkout-session-analytics')
def setup(db: Session = Depends(get_DB)):
    try:
        # Delete all information on the table
        db.query(models.CheckoutDuration).delete()
        db.query(models.TopProductWeekly).delete()
        db.commit()
        return {'message': 'PopularityIndex cleaned'}
    
    except Exception as e:
        # Rollback if any error happens
        db.rollback()  
        return {"error": str(e)}
    
    
@app.get('/clean-popularity')
def setup(db: Session = Depends(get_DB)):
    try:
        # Delete all information on the table
        db.query(models.PopularityIndex).delete()
        db.commit()
        return {'message': 'PopularityIndex cleaned'}
    
    except Exception as e:
        # Rollback if any error happens
        db.rollback()  
        return {"error": str(e)}

@app.get('/clean-click-interactions')
def setup(db: Session = Depends(get_DB)):
    try:
        # Delete all information on the table
        db.query(models.ClickInteraction).delete()
        db.commit()
        return {'message': 'click-interactions cleaned'}
    
    except Exception as e:
        # Rollback if any error happens
        db.rollback()  
        return {"error": str(e)}

@app.get('/clean-search-analytics')
def setup(db: Session = Depends(get_DB)):
    try:
        # Delete all information on the table
        db.query(models.SearchesAnalytics).delete()
        db.commit()
        return {'message': 'search-analytics cleaned'}
    
    except Exception as e:
        # Rollback if any error happens
        db.rollback()  
        return {"error": str(e)}

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
