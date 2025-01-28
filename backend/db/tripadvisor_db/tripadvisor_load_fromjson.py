import mysql.connector
import json

# Connect to MySQL
db_config = mysql.connector.connect(
    host="localhost",  # Correct syntax
    port=3306, 
    user="root",
    password="fuka1010",
    database="tripadvisor_db"

)
cursor=db_config.cursor()



# Insert restaurant data
with open('tripadvisor_data.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

for item in data:
    cursor.execute("""
        INSERT INTO restaurants (name, description, latitude, longitude, rating, review_count, price_level, cuisine_types, meal_types, features, tags)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    """, (
        item.get('name'),
        item.get('description'),
        item.get('latitude'),
        item.get('longitude'),
        item.get('rating'),
        item.get('numberOfReviews'),
        item.get('priceLevel'),
        json.dumps(item.get('cuisines', [])),
        json.dumps(item.get('mealTypes', [])),
        json.dumps(item.get('features', [])),
        json.dumps(item.get('reviewTags', []))
    ))

db_config.commit()
cursor.close()
db_config.close()
print("Data loaded into MySQL successfully.")