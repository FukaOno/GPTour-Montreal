import os
import csv
import mysql.connector
from mysql.connector import Error


DB_CONFIG = {
    'host': 'localhost',
    'database': 'attraction',
    'user': 'root',
    'password': 'fuka1010'
}

def create_connection():
    return mysql.connector.connect(
        host=DB_CONFIG['host'],
        database=DB_CONFIG['database'],
        user=DB_CONFIG['user'],
        password=DB_CONFIG['password'],
        charset= 'utf8mb4',
        collation='utf8mb4_unicode_ci'
    )


def parse_csv(file_name):
    script_dir = os.path.dirname(os.path.abspath(__file__))
    file_path = os.path.join(script_dir, file_name)

    try:
        with open('attraction.csv', 'rb') as f:
            print(f.read(100))
        # with open(file_path, 'r', encoding='utf-8') as f:
        #     return list(csv.DictReader(f))

    except FileNotFoundError:
        print(f"Error: Could not find CSV file at {file_path}")
        raise

def insert_place(conn, row):

    sql = """INSERT INTO Place (
        id, full_address, city, country, postal_code, street1, street2, category,
        description, email, image_url, latitude, longitude, local_address,
        local_lang_code, local_name, location_string, name, num_reviews, phone,
        photo_count, ranking_denominator, ranking_position, ranking_string, rating,
        rating_count1, rating_count2, rating_count3, rating_count4, rating_count5,
        raw_ranking, traveler_choice_award, place_type, web_url, website, lowest_price
    ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s,
        %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"""
    

    values = (
        int(row.get('id', 0)),
        row.get('address', ''),  
        row.get('addressObj/city', ''),
        row.get('addressObj/country', ''),
        row.get('addressObj/postalcode', ''),
        row.get('addressObj/street1', ''),
        row.get('addressObj/street2', ''),
        row.get('category', ''),
        row.get('description', ''),
        row.get('email', ''),
        row.get('image', ''),
        float(row.get('latitude', 0)) if row.get('latitude') else None,
        float(row.get('longitude', 0)) if row.get('longitude') else None,
        row.get('localAddress', ''),
        row.get('localLangCode', ''),
        row.get('localName', ''),
        row.get('locationString', ''),
        row.get('name', ''),
        int(row.get('numberOfReviews', 0)),
        row.get('phone', ''),
        int(row.get('photoCount', 0)),
        int(row.get('rankingDenominator', 0)) if row.get('rankingDenominator') else None,
        int(row.get('rankingPosition', 0)) if row.get('rankingPosition') else None,
        row.get('rankingString', ''),
        float(row.get('rating', 0)) if row.get('rating') else None,
        int(row.get('ratingHistogram/count1', 0)),
        int(row.get('ratingHistogram/count2', 0)),
        int(row.get('ratingHistogram/count3', 0)),
        int(row.get('ratingHistogram/count4', 0)),
        int(row.get('ratingHistogram/count5', 0)),
        float(row.get('rawRanking', 0)) if row.get('rawRanking') else None,
        bool(row.get('travelerChoiceAward', False)),
        row.get('type', ''),
        row.get('webUrl', ''),
        row.get('website', ''),
        float(row.get('offerGroup/lowestPrice', '0').replace('CA$', '').replace(',', '')) if row.get('offerGroup/lowestPrice') else None
    )
    
    try:
        with conn.cursor() as cursor:
            cursor.execute(sql, values)
            conn.commit()
    except Exception as e:
        print(f"Error inserting place: {e}")
        print(f"Problematic values: {values}")
        raise

def insert_metro_station(conn, place_id, station_num, row):
    prefix = f'nearestMetroStations/{station_num}/'
    
    
    station_sql = """INSERT INTO MetroStation (
        place_id, station_order, address, distance, latitude, longitude,
        local_address, local_name, name
    ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)"""
    
    station_values = (
        place_id,
        station_num,
        row.get(prefix + 'address'),
        float(row.get(prefix + 'distance')) if row.get(prefix + 'distance') else None,
        float(row.get(prefix + 'latitude')) if row.get(prefix + 'latitude') else None,
        float(row.get(prefix + 'longitude')) if row.get(prefix + 'longitude') else None,
        row.get(prefix + 'localAddress'),
        row.get(prefix + 'localName'),
        row.get(prefix + 'name')
    )

    try:
        with conn.cursor() as cursor:
            cursor.execute(station_sql, station_values)
            station_id = cursor.lastrowid
            conn.commit()
    except Error as e:
        print(f"Error inserting metro station: {e}")
        raise

    
    # Insert MetroLines for this station
    for line_num in range(2):  # Assuming max 2 lines per station
        line_prefix = prefix + f'lines/{line_num}/'
        line_sql= None

        if row.get(line_prefix + 'lineName'):
            line_sql = """INSERT INTO MetroLine (
                metro_station_id, line_order, line_id, line_name, line_symbol,
                system_name, system_symbol, line_type
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)"""
            
            line_values = (
                station_id,
                line_num,
                row.get(line_prefix + 'id'),
                row.get(line_prefix + 'lineName'),
                row.get(line_prefix + 'lineSymbol'),
                row.get(line_prefix + 'systemName'),
                row.get(line_prefix + 'systemSymbol'),
                row.get(line_prefix + 'type')
            )
            
        try:
            with conn.cursor() as line_cursor:
                    line_cursor.execute(line_sql, line_values)
                    conn.commit()
        except Error as e:
            print(f"Error inserting metro line: {e}")
            raise

def clean_text(text):
    return text.encode('latin-1').decode('utf-8', errors='ignore')


def insert_offer(conn, place_id, offer_num, row):
    prefix = f'offerGroup/offerList/{offer_num}/'
    sql = """INSERT INTO Offer (
        place_id, offer_order, image_url, offer_type, partner, price,
        primary_category, product_code, rounded_price, title, url, description
    ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"""

    url = row.get(prefix + 'url', '')[:4000]
    title = clean_text(row.get(prefix + 'title', ''))[:500]
    
    values = (
        place_id,
        offer_num,
        row.get(prefix + 'imageUrl', '')[:4000],
        row.get(prefix + 'offerType', ''),
        row.get(prefix + 'partner', ''),
        float(row.get(prefix + 'price', '0').replace('CA$', '').replace(',', ''))  if row.get(prefix + 'price') else None,
        row.get(prefix + 'primaryCategory', ''),
        row.get(prefix + 'productCode', ''),
        float(row.get(prefix + 'roundedUpPrice').replace('CA$', '').replace(',', ''))  if row.get(prefix + 'roundedUpPrice') else None,
        title, 
        url,
        row.get(prefix + 'description', '')[:4000]
    )
    
    with conn.cursor() as cursor:
        cursor.execute(sql, values)
    conn.commit()

def insert_photo(conn, place_id, photo_order, url):
    sql = "INSERT INTO Photo (place_id, photo_url, photo_order) VALUES (%s, %s, %s)"
    with conn.cursor() as cursor:
        cursor.execute(sql, (place_id, url, photo_order))
    conn.commit()

def main():
    conn = create_connection()
    data = parse_csv('attraction.csv')

    try:
        for row in data:
            place_id = int(row['id'])
            
            check_sql = "SELECT id FROM Place WHERE id = %s"
            with conn.cursor() as cursor:
                cursor.execute(check_sql, (place_id,))
                if cursor.fetchone():
                    print(f"Skipping all data for duplicate ID {place_id}")
                    continue  # Skip entire record
            insert_place(conn, row)
            

            # Insert related data
            # Metro Stations (0-4)
            for station_num in range(5):
                if row.get(f'nearestMetroStations/{station_num}/address'):
                    insert_metro_station(conn, place_id, station_num, row)
            
            # Photos (0-59)
            for photo_num in range(60):
                if row.get(f'photos/{photo_num}'):
                    insert_photo(conn, place_id, photo_num, row[f'photos/{photo_num}'])
            
            # Offers (0-4)
            for offer_num in range(5):
                if row.get(f'offerGroup/offerList/{offer_num}/title'):
                    insert_offer(conn, place_id, offer_num, row)
            
 
    except Error as e:
        print(f"Database Error: {e}")
        conn.rollback()
    except Exception as e:
        print(f"General Error: {e}")
    finally:
        if conn.is_connected():
            conn.close()

if __name__ == '__main__':
    main()