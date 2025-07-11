import os
import re
import json
import pandas as pd
from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from dotenv import load_dotenv
from data_manager import RestaurantDataManager, get_day_part
from ai_tools import RestaurantConcierge, conversation_history
from flask_compress import Compress

# Load environment variables
load_dotenv()

app = Flask(__name__, static_folder='static')
CORS(app)
Compress(app) 

# Configure Database
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', 'sqlite:///chat_history.db')  
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Initialize concierge
concierge = RestaurantConcierge()

# Load restaurant data on startup
YELP_API_KEY = os.getenv("YELP_API_KEY")
if YELP_API_KEY:
    concierge.data_manager.load_restaurants('Los Angeles', 240)
else:
    print("Warning: Restaurant data file not found. Please ensure 'yelp_restaurants_full.json' exists.")

# Model for storing chat history
class ChatHistory(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.String(80), nullable=False)
    user_message = db.Column(db.String(500), nullable=False)
    bot_response = db.Column(db.String(500), nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<ChatHistory {self.user_id} - {self.user_message} - {self.bot_response}>'

# Create tables if not already created
with app.app_context():
    db.create_all()  

# Chat queue for batch database writes
app.chat_queue = []

@app.route('/')
def index():
    return render_template('index4_1.html')

@app.route('/chat', methods=['POST'])
def chat_endpoint():
    """Enhanced chat endpoint with batch database writes"""
    try:
        # Check if user_id exists in URL parameters, fallback to 'default_user' if missing
        user_id = request.args.get('user_id', 'default_user')
        data = request.json
        user_message = data.get('message', '')

        if not user_message:
            return jsonify({'error': 'No message provided in JSON body'}), 400

        # Process message through concierge to get the bot's response
        response = concierge.chat(user_message)
        
        # Ensure response is a string
        if not isinstance(response, str):
            response = str(response)

        # Create chat entry
        chat_entry = ChatHistory(
            user_id=user_id, 
            user_message=user_message, 
            bot_response=response
        )
        
        # Add to batch queue
        app.chat_queue.append(chat_entry)
        
        # Commit every 5 entries to reduce database writes
        if len(app.chat_queue) >= 5:
            try:
                db.session.bulk_save_objects(app.chat_queue)
                db.session.commit()
                app.chat_queue = []
            except Exception as e:
                print(f"Error in batch save: {e}")
                app.chat_queue = []

        return jsonify({
            'user_id': user_id,
            'response': response,
            'timestamp': datetime.now().isoformat()
        })

    except Exception as e:
        # Handle any other errors
        error_response = "Our service is temporarily unavailable. Please try again in a moment."
        return jsonify({
            'user_id': user_id,
            'response': error_response,
            'timestamp': datetime.now().isoformat()
        })

@app.route('/get_user_chat_history', methods=['GET'])
def get_user_chat_history():
    """Get chat history for a specific user"""
    try:
        user_id = request.args.get('user_id', 'default_user')  
        chat_history = ChatHistory.query.filter_by(user_id=user_id).all()

        history = [{
            'user_id': entry.user_id,
            'user_message': entry.user_message,
            'bot_response': entry.bot_response,
            'timestamp': entry.timestamp.isoformat()
        } for entry in chat_history]

        return jsonify({'chat_history': history, 'user_id': user_id})

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/trending', methods=['GET'])
def get_trending_restaurants():
    """Get currently trending restaurants using precomputed scores"""
    try:
        show_future = request.args.get('future', 'false').lower() == 'true'
       
        # Get top trending restaurants using precomputed scores
        trending_data = []
        count = 0
        
        for restaurant in concierge.data_manager.restaurants_data:
            if count >= 20:  # Only process top candidates
                break
                
            # Use precomputed scores
            rid = restaurant.get('id')
            if not rid:
                continue
                
            scores = concierge.data_manager.precomputed_scores.get(rid, (0, 0))
            hype_score = scores[0]
            
            if hype_score > 70:  # Only high-hype restaurants
                restaurant_data = {
                    'id': restaurant.get('id'),
                    'alias': restaurant.get('alias'),
                    'name': restaurant.get('name'),
                    'is_closed': restaurant.get('is_closed', False),
                    'category': ", ".join([cat['title'] for cat in restaurant.get('categories', [])]),
                    'price': restaurant.get('price', 'N/A'),
                    'phone': restaurant.get('phone', 'N/A'),
                    'display_phone': restaurant.get('display_phone', 'N/A'),
                    'distance': round(restaurant.get('distance', 0)),
                    'business_hours': restaurant.get('business_hours', []),
                    'url': restaurant.get('url'),
                    'image_url': restaurant.get('image_url'),
                    'rating': restaurant.get('rating'),
                    'hype_score': round(hype_score, 1),
                    'review_count': restaurant.get('review_count'),
                    'transaction_types': ", ".join(restaurant.get('transactions', [])),
                    'address': ", ".join(restaurant.get('location', {}).get('display_address', [])),
                    'city': restaurant.get('location', {}).get('city', ''),
                    'state': restaurant.get('location', {}).get('state', ''),
                    'zip_code': restaurant.get('location', {}).get('zip_code', ''),
                    'country': restaurant.get('location', {}).get('country', ''),
                    'business_hours': restaurant.get('business_hours', []),
                    'attributes': restaurant.get('attributes', {}),
                    'coordinates': restaurant.get('coordinates', {}),
                    'location': restaurant.get('location', {})
                }
               
                # Only add future trend data if explicitly requested
                if show_future:
                    restaurant_data['future_trend'] = round(scores[1], 1)
                    restaurant_data['prediction'] = 'Rising Star' if scores[1] > hype_score + 5 else 'Currently Hot'
                
                trending_data.append(restaurant_data)
                count += 1
       
        # Sort by current hype score (or future trend if requested)
        sort_key = 'future_trend' if show_future else 'hype_score'
        trending_data.sort(key=lambda x: x.get(sort_key, 0), reverse=True)
       
        return jsonify({
            'trending_restaurants': trending_data[:10],
            'showing_future_predictions': show_future,
            'timestamp': datetime.now().isoformat()
        })
   
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/health')
def health_check():
    """Enhanced health check with model status"""
    return jsonify({
        'status': 'healthy',
        'restaurants_loaded': len(concierge.data_manager.restaurants_data),
        'vectorstore_ready': concierge.data_manager.vectorstore is not None,
        'hype_model_ready': concierge.data_manager.hype_model is not None,
        'trend_model_ready': concierge.data_manager.trend_model is not None,
        'yelp_api_available': YELP_API_KEY is not None,
        'conversation_history_length': len(conversation_history),
        'current_time': get_day_part(),
        'timestamp': datetime.now().isoformat()
    })

@app.route('/analytics', methods=['GET'])
def get_analytics():
    """Get user selection analytics"""
    try:
        if not os.path.exists(concierge.data_manager.csv_file):
            return jsonify({'message': 'No analytics data available'})
        
        df = pd.read_csv(concierge.data_manager.csv_file)
        
        analytics = {
            'total_selections': len(df),
            'popular_cuisines': df['categories'].value_counts().head(5).to_dict() if 'categories' in df.columns else {},
            'average_rating': df['rating'].mean() if 'rating' in df.columns else 0,
            'price_distribution': df['price'].value_counts().to_dict() if 'price' in df.columns else {},
            'recent_selections': df.tail(10).to_dict('records') if len(df) > 0 else [],
            'timestamp': datetime.now().isoformat()
        }
        
        return jsonify(analytics)
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/reset_conversation', methods=['POST'])
def reset_conversation():
    """Reset conversation history"""
    global conversation_history
    conversation_history = []
    concierge.conversation_stage = "greeting"
    concierge.memory.clear()
    
    return jsonify({
        'message': 'Conversation reset successfully',
        'timestamp': datetime.now().isoformat()
    })

if __name__ == "__main__":
    print("🍽️ Starting Enhanced Restaurant AI Concierge...")
    print(f"Current time period: {get_day_part()}")
    print(f"Yelp API available: {'Yes' if YELP_API_KEY else 'No'}")
    print(f"Database: {app.config['SQLALCHEMY_DATABASE_URI']}")
    app.run(debug=True, host='0.0.0.0', port=5000)
