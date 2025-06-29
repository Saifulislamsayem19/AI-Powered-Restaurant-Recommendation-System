# AI-Powered-Restaurant-Recommendation-System
Restaurant Concierge is an advanced AI-powered recommendation system specifically designed for Los Angeles diners. The system combines natural language processing, machine learning, and vector similarity search to provide intelligent, contextual restaurant recommendations based on user preferences, location, cuisine types, and trending metrics.


![image](https://github.com/user-attachments/assets/713beb69-fcfc-4bfb-bf6a-39a89c09b37b)


## ✨ Key Features

- **Intelligent Query Processing**: Understands complex natural language requests about restaurants
- **Trend Analysis**: Identifies trending restaurants using proprietary hype and trend scoring algorithms
- **Special Event Planning**: Creates custom dining plans for special occasions
- **Location-Based Recommendations**: Suggests restaurants based on neighborhoods or landmarks
- **Time-Sensitive Suggestions**: Recommends open restaurants based on current time
- **Restaurant Comparisons**: Compares multiple restaurants across various metrics
- **Conversational Interface**: Maintains context throughout multi-turn conversations

## 🛠️ Technology Stack

- **Backend**: Python, Flask
- **Database**: SQLAlchemy, SQLite
- **Natural Language Processing**: LangChain, OpenAI APIs
- **Machine Learning**: Scikit-learn (RandomForest, GradientBoosting)
- **Vector Search**: FAISS for semantic similarity
- **External Data**: Yelp Fusion API
- **Web Interface**: HTML/JavaScript

## 📋 Installation

```bash
# Clone the repository
git clone https://github.com/yourusername/la-foodie-concierge.git
cd la-foodie-concierge

# Create and activate virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Set up environment variables
cp .env.example .env
# Edit .env file with your API keys
```

### Environment Variables

Create a `.env` file with the following variables:

```
YELP_API_KEY=your_yelp_api_key
OPENAI_API_KEY=your_openai_api_key
DATABASE_URL=sqlite:///chat_history.db  # Or your preferred database URL
```

## 🚀 Usage

### Starting the Server

```bash
python app.py
```

The server will start on http://localhost:5000

### API Endpoints

- **GET /** - Web interface
- **POST /chat** - Send user messages and get AI responses
- **GET /trending** - Get trending restaurants
- **GET /get_user_chat_history** - Retrieve chat history for a user
- **GET /health** - Check system health and model status
- **GET /analytics** - Get user selection analytics
- **POST /reset_conversation** - Reset the conversation history

## 💡 How It Works

### Data Pipeline

1. **Data Collection**: Loads restaurant data from Yelp API or local JSON dataset
2. **Vectorization**: Converts restaurant details into embeddings for semantic search
3. **Model Training**: Trains hype and trend prediction models using restaurant attributes

### Recommendation Engine

- **Query Analysis**: Uses LLM to extract intent, cuisine preferences, location, etc.
- **Restaurant Matching**: Combines filters and vector similarity to find matching restaurants
- **Scoring**: Ranks restaurants based on ratings, reviews, and ML-predicted trend scores
- **Response Generation**: Creates natural language responses with recommendations

### ML Scoring System

- **Hype Score**: Measures current popularity based on ratings, reviews, location, etc.
- **Trend Score**: Predicts future popularity using machine learning models
- **Popularity Prediction**: Classifies restaurants as "Rising Star", "Hot Right Now", etc.

## 📊 Project Structure

```
la-foodie-concierge/
├── app.py                 # Main Flask application
├── data_manager.py        # Restaurant data and model management
├── ai_tools.py            # Conversation and recommendation logic
├── requirements.txt       # Project dependencies
├── static/                # Static web assets
│   └── index4_1.html      # Web interface
└── saved_models/          # Directory for trained models
    ├── vectorstore/       # FAISS vector store
    ├── hype_model.pkl     # Hype prediction model
    ├── trend_model.pkl    # Trend prediction model
    ├── scaler.pkl         # Feature scaling for models
    └── menu_cache.json    # Cached menu data
```

## 🔍 Example Queries

- "What are the trending restaurants in Silver Lake right now?"
- "I need a romantic Italian restaurant in Santa Monica for tonight"
- "Show me the top hidden gems in Downtown LA"
- "Plan a dinner for 6 people in Venice for my birthday tomorrow"
- "Compare Bestia and Felix Trattoria"
- "What's open for late night food near Hollywood Bowl?"

## 📝 Future Improvements

- [ ] Add user authentication system
- [ ] Implement actual reservation booking via third-party APIs
- [ ] Create mobile application with location awareness
- [ ] Add photo gallery and menu preview capabilities
- [ ] Integrate with Google Maps for directions
- [ ] Expand to additional cities beyond Los Angeles

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🤝 Acknowledgements

- Yelp Fusion API for restaurant data
- OpenAI for language model capabilities
- LangChain for NLP frameworks

---

Experience smarter dining decisions today! 🍽️✨
