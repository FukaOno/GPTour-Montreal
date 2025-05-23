import os
from flask import Flask, request, Response, jsonify
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import or_, and_
from dotenv import load_dotenv
from flask_cors import CORS
from openai import OpenAI
import uuid
import json
from datetime import datetime, timedelta
import re
from dateutil.parser import parse


key = os.getenv("KEY")

load_dotenv()

app = Flask(__name__)
CORS(app)
app.debug = True

# Database Configuration
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv("DB_URI")
app.config['SQLALCHEMY_BINDS'] = {
    'hotel': os.getenv("DB_URI_HOTEL")
    # 'attraction': os.getenv("DB_URI_ATTRACTION")

}
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)


# Event Model
class Event(db.Model):
    __tablename__ = 'events'  
    id = db.Column(db.Integer, primary_key=True)
    titre = db.Column(db.String(255))
    url_fiche = db.Column(db.Text)
    description = db.Column(db.Text)
    date_debut = db.Column(db.Date)
    date_fin = db.Column(db.Date)
    type_evenement = db.Column(db.String(100))
    public_cible = db.Column(db.String(100))
    emplacement = db.Column(db.String(100))
    inscription = db.Column(db.String(50))
    cout = db.Column(db.String(50))
    arrondissement = db.Column(db.String(100))
    titre_adresse = db.Column(db.String(255))
    adresse_principale = db.Column(db.Text)
    adresse_secondaire = db.Column(db.Text)
    code_postal = db.Column(db.String(10))
    latitude = db.Column(db.Numeric(10, 8), nullable=False, default=45.5017)
    longitude = db.Column(db.Numeric(11, 8), nullable=False, default=-73.5673)
    coord_x = db.Column(db.Numeric(10, 1))
    coord_y = db.Column(db.Numeric(10, 1))
    created_at = db.Column(db.TIMESTAMP)

    def serialize(self):
        return {
            "name": self.titre,
            "start_date": str(self.date_debut),
            "end_date": str(self.date_fin),
            "type": self.type_evenement,
            "price": self.cout or "Free",
            "latitude": float(self.latitude) if self.latitude else None,
            "longitude": float(self.longitude) if self.longitude else None,
            "registration_required": self.inscription == "Required",
            "arrondissement": self.arrondissement
        }

client = OpenAI(api_key=key, base_url="https://api.deepseek.com")


# Hotel Model
class Hotel(db.Model):
    __bind_key__ = 'hotel'
    __tablename__ = 'Hotels'
    hotel_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(255))
    description = db.Column(db.Text)
    address_street1 = db.Column(db.String(255))
    city = db.Column(db.String(100))
    country = db.Column(db.String(100))
    postal_code = db.Column(db.String(20))
    latitude = db.Column(db.Numeric(9, 6))
    longitude = db.Column(db.Numeric(9, 6))
    hotel_class = db.Column(db.Numeric(3, 1))
    hotel_class_attribution = db.Column(db.String(255))
    main_image_url = db.Column(db.String(255))
    phone = db.Column(db.String(50))
    website = db.Column(db.String(255))
    web_url = db.Column(db.String(255))
    price_level = db.Column(db.String(10))
    price_range = db.Column(db.String(100))
    ranking_denominator = db.Column(db.Integer)
    ranking_position = db.Column(db.Integer)
    ranking_string = db.Column(db.String(255))
    rating = db.Column(db.Numeric(3, 2))
    
    # Relationships
    photos = db.relationship('Photo', backref='hotel', lazy=True)
    review_scores = db.relationship('ReviewScore', backref='hotel', lazy=True)
    metro_stations = db.relationship('MetroStation', backref='hotel', lazy=True)

class MetroLine(db.Model):
    __bind_key__ = 'hotel'
    __tablename__ = 'MetroLines'
    metro_line_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    metro_station_id = db.Column(db.Integer, db.ForeignKey('MetroStations.metro_station_id'))
    line_id = db.Column(db.String(50))
    line_name = db.Column(db.String(255))
    line_symbol = db.Column(db.String(50))
    system_symbol = db.Column(db.String(50))

class MetroStation(db.Model):
    __bind_key__ = 'hotel'
    __tablename__ = 'MetroStations'
    metro_station_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    hotel_id = db.Column(db.Integer, db.ForeignKey('Hotels.hotel_id'))
    name = db.Column(db.String(255))
    address = db.Column(db.String(255))
    distance = db.Column(db.String(50))
    latitude = db.Column(db.Numeric(9, 6))
    longitude = db.Column(db.Numeric(9, 6))
    
    metro_lines = db.relationship('MetroLine', backref='metro_station', lazy=True)

class Photo(db.Model):
    __bind_key__ = 'hotel'
    __tablename__ = 'Photos'
    photo_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    hotel_id = db.Column(db.Integer, db.ForeignKey('Hotels.hotel_id'))
    photo_url = db.Column(db.String(255))
    photo_order = db.Column(db.Integer)

class ReviewScore(db.Model):
    __bind_key__ = 'hotel'
    __tablename__ = 'ReviewScores'
    review_score_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    hotel_id = db.Column(db.Integer, db.ForeignKey('Hotels.hotel_id'))
    category_name = db.Column(db.String(255))
    score = db.Column(db.Numeric(5, 2))
    category_order = db.Column(db.Integer)


# # Attraction Models (using 'attraction' bind key)
# # --------------------------------------------------
# class MetroStation(db.Model):
#     __bind_key__ = 'attraction'
#     __tablename__ = 'MetroStation'
#     id = db.Column(db.Integer, primary_key=True, autoincrement=True)
#     metro_station_id = db.Column(db.Integer)
#     line_order = db.Column(db.Integer)
#     line_id = db.Column(db.String(255))
#     line_name = db.Column(db.String(255))
#     line_symbol = db.Column(db.String(255))
#     system_name = db.Column(db.String(255))
#     system_symbol = db.Column(db.String(255))
#     line_type = db.Column(db.String(255))

# class MetroLine(db.Model):
#     __bind_key__ = 'attraction'
#     __tablename__ = 'MetroLine'
#     id = db.Column(db.Integer, primary_key=True, autoincrement=True)
#     metro_station_id = db.Column(db.Integer, db.ForeignKey('MetroStation.id'))
#     line_order = db.Column(db.Integer)
#     line_id = db.Column(db.String(255))
#     line_name = db.Column(db.String(255))
#     line_symbol = db.Column(db.String(255))
#     system_name = db.Column(db.String(255))
#     system_symbol = db.Column(db.String(255))
#     line_type = db.Column(db.String(255))

# class Place(db.Model):
#     __bind_key__ = 'attraction'
#     __tablename__ = 'Place'
#     id = db.Column(db.Integer, primary_key=True)
#     # [Keep all Place columns from your schema]
#     # Add relationships
#     offers = db.relationship('Offer', backref='place')
#     photos = db.relationship('Photo', backref='place')

# class Offer(db.Model):
#     __bind_key__ = 'attraction'
#     __tablename__ = 'Offer'
#     id = db.Column(db.Integer, primary_key=True, autoincrement=True)
#     place_id = db.Column(db.Integer, db.ForeignKey('Place.id'))
#     # [Keep all Offer columns from your schema]

# class Photo(db.Model):
#     __bind_key__ = 'attraction'
#     __tablename__ = 'Photo'
#     id = db.Column(db.Integer, primary_key=True, autoincrement=True)
#     place_id = db.Column(db.Integer, db.ForeignKey('Place.id'))
#     # [Keep all Photo columns from your schema]



# Add these new functions
def get_hotels_with_details(limit=15):
    try:
        return Hotel.query.options(
            db.joinedload(Hotel.photos),
            db.joinedload(Hotel.review_scores),
            db.joinedload(Hotel.metro_stations).joinedload(MetroStation.metro_lines)
        ).limit(limit).all()
    except Exception as e:
        print(f"Hotel query error: {str(e)}")
        return []

def format_hotels_for_gpt(hotels):
    if not hotels:
        return "No hotel data available"
    
    hotel_list = []
    for hotel in hotels:
        entry = f"""**{hotel.name}** (Rating: {hotel.rating}/5)
- Address: {hotel.address_street1}, {hotel.city}
- Price Range: {hotel.price_range or 'Not specified'}
- Class: {hotel.hotel_class}/5
- Metro Access: {', '.join([f"{station.name} ({', '.join(line.line_name for line in station.metro_lines)})" 
                          for station in hotel.metro_stations]) or 'None nearby'}
- Top Amenities: {', '.join([score.category_name for score in hotel.review_scores][:3])}"""
        hotel_list.append(entry)
    
    return "AVAILABLE HOTELS:\n" + "\n\n".join(hotel_list)

def is_hotel_query(user_message, hotels):
    user_msg = user_message.lower()
    hotel_names = [h.name.lower() for h in hotels]
    keywords = {
        'hotel', 'stay', 'lodging', 'accommodation',
        'book a room', 'where to stay', 'place to stay',
        'recommend hotels', 'find hotels', 'hotel near'
    }
    hotel_names = [h.name.lower() for h in hotels]
    
    return any(kw in user_msg for kw in keywords) or any(name in user_msg for name in hotel_names)


# trip planning detection function
def is_trip_planning(user_message):
    trip_keywords = {
        'plan my trip', 'itinerary', 'visit montreal', 
        'vacation plan', 'travel plan', 'schedule my visit'
    }
    return any(kw in user_message.lower() for kw in trip_keywords)

# def get_attractions_with_details(limit=15):
#     return Place.query.options(
#         db.joinedload(Place.offers),
#         db.joinedload(Place.photos),
#         db.joinedload(Place.metro_stations).joinedload(MetroStation.metro_lines)
#     ).limit(limit).all()

# def format_attractions_for_gpt(places):
#     if not places:
#         return "No attraction data available"
    
#     place_list = []
#     for place in places:
#         entry = f"""🏛️ **{place.name}** (Rating: {place.rating}/5)
# - Address: {place.full_address}
# - Category: {place.category}
# - Metro Stations: {', '.join([station.line_name for station in place.metro_stations]) if place.metro_stations else 'None nearby'}
# - Offers: {len(place.offers)} available deals"""
#         place_list.append(entry)
    
#     return "ATTRACTIONS & LANDMARKS:\n" + "\n\n".join(place_list)

# def is_attraction_query(user_message):
#     attraction_keywords = {
#         'attraction', 'landmark', 'museum', 'gallery',
#         'monument', 'place to visit', 'things to see',
#         'points of interest', 'tourist spot', 'metro station'
#     }
#     return any(kw in user_message.lower() for kw in attraction_keywords)

# GPT endpoint
@app.route("/gpt", methods=["POST"])
def convo():
    data = request.get_json()
    user_message = data.get('user_message', '').lower()
    session_id = data.get("session_id") or str(uuid.uuid4())

    try:
        # First determine query type
        hotels = get_hotels_with_details()
        is_hotel = is_hotel_query(user_message, hotels)
        is_metro = "metro" in user_message or "station" in user_message
        # is_attraction = is_attraction_query(user_message)

        # attractions = get_attractions_with_details()
        # events = get_events_by_date(start_date, end_date) if date_range_required else []

        # context = []
        # if is_hotel: context.append(format_hotels_for_gpt(hotels))
        # if is_attraction_query(user_message): context.append(format_attractions_for_gpt(attractions))
        # if not any([is_hotel, is_metro, is_attraction]): context.append(format_events_for_gpt(events))

        # # Dynamic system prompt
        # system_prompt = f"""MONTREAL TRAVEL ASSISTANT MODE:
        # {"".join(context)}
        
        # Requirements:
        # 1. Combine information from hotels, attractions{" and events" if events else ""}
        # 2. Prioritize locations with metro access
        # 3. Mention relevant offers/deals where applicable
        # 4. {"Include date-specific events" if events else "Focus on permanent locations"}"""

        # Only extract dates if needed
        date_range_required = not (is_hotel or is_metro)
        start_date_str = end_date_str = None

        if date_range_required:
            # Date extraction logic for event planning
            start_date_str = data.get('start_date')
            end_date_str = data.get('end_date')
            
            if not start_date_str or not end_date_str:
                msg_start, msg_end = extract_dates_from_message(user_message)
                if msg_start and msg_end:
                    start_date_str = msg_start.isoformat()
                    end_date_str = msg_end.isoformat()
                else:
                    raise ValueError("Date range required for event planning")

            start_date = datetime.strptime(start_date_str, '%Y-%m-%d').date()
            end_date = datetime.strptime(end_date_str, '%Y-%m-%d').date()
            events = get_events_by_date(start_date, end_date)
            event_context = format_events_for_gpt(events)
        else:
            events = []
            event_context = ""

        # Build system prompt based on query type
        hotel_context = format_hotels_for_gpt(hotels)
        
        if is_metro:
            system_prompt = f"""METRO LOCATOR MODE:
            Available Hotels with Metro Access:
            {hotel_context}
            
            Requirements:
            1. Identify metro stations near mentioned locations
            2. Include line information
            3. Ignore date references"""
            
        elif is_hotel:
            system_prompt = f"""HOTEL SEARCH MODE:
            {hotel_context}
            
            Requirements:
            1. Recommend hotels matching the request
            2. Focus on metro access
            3. Ignore date references"""
            
        else:
            system_prompt = f"""TRIP PLANNING MODE:
            {hotel_context}
            {event_context}
            
            Requirements:
            1. Create date-specific itineraries"""

        # Session management
        if session_id not in sessions:
            sessions[session_id] = {
                "conversation": [{"role": "system", "content": system_prompt}],
                "last_activity": datetime.now()
            }
        else:
            sessions[session_id]["conversation"][0]["content"] = system_prompt
            sessions[session_id]["last_activity"] = datetime.now()

        sessions[session_id]["conversation"].append(
            {"role": "user", "content": user_message}
        )

        # Response generation
        def generate():
            full_response = []
            stream = client.chat.completions.create(
                model="deepseek-chat",
                messages=sessions[session_id]["conversation"],
                stream=True
            )
            
            for chunk in stream:
                if chunk.choices[0].delta.content:
                    full_response.append(chunk.choices[0].delta.content)
                    yield f"data: {json.dumps({'content': chunk.choices[0].delta.content})}\n\n"
            
            sessions[session_id]["conversation"].append(
                {"role": "assistant", "content": ''.join(full_response)}
            )
            yield "data: [DONE]\n\n"
        
        return Response(generate(), mimetype="text/event-stream")

    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 500




sessions = {}

def initialize_session(session_id, date_context=""):
    sessions[session_id] = {
        "conversation": [{
            "role": "system",
            "content": f"""Respond using ONLY these events:
            {date_context}
            
            Requirements:
            1. Create hourly itineraries for requested dates
            2. Include exact event times if available
            3. Note transportation between locations
            4. Flag events needing registration
            5. Never invent fictional events"""
        }],
        "last_activity": datetime.now()
    }

#add automatic cleanup for inactive sessions
def cleanup_sessions():
    now = datetime.now()
    expired = [
        sid for sid, data in sessions.items() 
        if (now - data["last_activity"]) > timedelta(hours=1)
    ]
    for sid in expired:
        del sessions[sid]

def get_events_by_date(start_date, end_date):
    try:
        return Event.query.filter(
            Event.date_debut.between(start_date, end_date)  # Only events STARTING in range
        ).order_by(Event.date_debut).limit(50).all()  # Limit to 50 most relevant
    except Exception as e:
        print(f"Database error: {str(e)}")
        return []

def format_events_for_gpt(events):
    if not events:
        return "No events found for these dates"
    
    event_list = []
    for event in events[:15]:
        # Handle null coordinates
        lat = float(event.latitude) if event.latitude else 45.5017  # Default to Montreal center
        lon = float(event.longitude) if event.longitude else -73.5673
        
        entry = f"""**{event.titre}**
        - Dates: {event.date_debut} to {event.date_fin}
        - Type: {event.type_evenement}
        - Price: {event.cout or 'Free'}
        - Coordinates: ({lat:.6f}, {lon:.6f})
        - Registration: {'Required' if event.inscription else 'Not required'}"""
        
        event_list.append(entry)
    
    return "CURRENT MONTREAL EVENTS:\n" + "\n\n".join(event_list)

def extract_dates_from_message(text):
    """Parse dates from natural language text"""
    date_patterns = [
    r"(\b(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\s*\d{1,2}\s*-\s*\d{1,2}\b)",  # May10-15 or May 10-15
    r"(\b\d{4}-\d{2}-\d{2}\s+to\s+\d{4}-\d{2}-\d{2}\b)"
]
    
    for pattern in date_patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            date_str = match.group(1)
            try:
                if '-' in date_str:
                    start_str, end_str = date_str.split('-', 1)
                    start_date = parse(start_str.strip(), fuzzy=True).date()
                    end_date = parse(end_str.strip(), fuzzy=True).date()
                    return start_date, end_date
                else:
                    single_date = parse(date_str, fuzzy=True).date()
                    return single_date, single_date
            except:
                continue
    return None, None


# @app.route("/gpt", methods=["POST"])
# def convo():
#     data = request.get_json()
    
#     # Extract dates
#     start_date_str = data.get('start_date')
#     end_date_str = data.get('end_date')
#     date_context = ""
    
#     if start_date_str and end_date_str:
#         try:
#             start_date = datetime.strptime(start_date_str, '%Y-%m-%d').date()
#             end_date = datetime.strptime(end_date_str, '%Y-%m-%d').date()
#             events = get_events_by_date(start_date, end_date)
#             date_context = format_events_for_gpt(events)

#             return {
#                 "event_count": len(events),
#                 "date_context_sample": date_context[:500] + "...",
#                 "system_prompt": sessions.get("conversation", [{}])[0].get("content", "")[:500] + "..."
#             }, 200
            
#         except Exception as e:
#             return {"error": f"Invalid date format: {str(e)}"}, 400


    # # Get or create session ID
    # session_id = data.get("session_id")
    # if not session_id or session_id not in sessions:
    #     session_id = str(uuid.uuid4())
    #     initialize_session(session_id)
    
    # conversation = sessions[session_id]["conversation"]
    
    # user_message = data.get("user_message")
    # if not user_message:
    #     return {"error": "Missing user_message"}, 400
    
    # conversation.append({"role": "user", "content": user_message})
    
    # # Create a generator for streaming responses
    # def generate():
    #     full_response = []
    #     stream = client.chat.completions.create(
    #         model="deepseek-chat",
    #         messages=conversation,
    #         stream=True
    #     )
        
    #     for chunk in stream:
    #         delta = chunk.choices[0].delta
    #         if delta.content:
    #             full_response.append(delta.content)
    #             yield f"data: {json.dumps({
    #                 'session_id': session_id,
    #                 'delta': delta.content,
    #                 'chunk_id': chunk.id,
    #                 'finished': False
    #             })}\n\n"
        
    #     conversation.append({"role": "assistant", "content": ''.join(full_response)})
    #     yield f"data: {json.dumps({
    #         'session_id': session_id,
    #         'finished': True
    #     })}\n\n"

    # return Response(generate(), mimetype="text/event-stream")



@app.route("/conversation/done", methods=["POST"])
def end_conversation():
    data = request.get_json()
    session_id = data.get("session_id")
    
    if not session_id:
        return {"error": "Missing session_id"}, 400
    
    if session_id in sessions:
        # Get conversation before deletion
        conversation = sessions[session_id]["conversation"]
        del sessions[session_id]
        return {
            "status": "success",
            "message": "Conversation ended",
            "session_id": session_id,
            "conversation_length": len(conversation)
        }, 200
    else:
        return {"error": "Invalid session_id"}, 404


@app.route("/test-db")
def test_db():
    try:
        event_count = Event.query.count()
        sample_event = Event.query.first()
        return {
            "status": "connected",
            "total_events": event_count,
            "sample_event": {
                "title": sample_event.titre,
                "dates": f"{sample_event.date_debut} to {sample_event.date_fin}"
            } if sample_event else None
        }
    except Exception as e:
        return {"error": str(e)}, 500

@app.route("/")
def home():
    return "Server is running!", 200

# Temporary test route to check data quality
@app.route("/test-event")
def test_event():
    event = Event.query.filter(
        Event.date_debut == '2025-02-02'
    ).first()
    
    if event:
        return jsonify({
            "exists": True,
            "event": event.serialize(),
            "raw_description": event.description[:100] + "..." if event.description else None
        })
    return jsonify({"exists": False})

if __name__ == "__main__":
    app.run(port=5001)