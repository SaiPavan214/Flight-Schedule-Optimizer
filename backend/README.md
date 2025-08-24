# Airport Operations API Backend

A FastAPI-based backend for the Next-Generation Airport Management & Flight Optimization Dashboard, featuring AI-powered flight search, real-time alerts, and runway optimization.

## 🚀 Features

- **Intelligent Flight Search**: Natural language processing using Google Gemini AI
- **Real-time Alerts**: Dynamic alerting system for airport operations
- **Runway Analytics**: Comprehensive runway utilization and optimization metrics
- **AI Chatbot**: Conversational interface powered by Gemini AI
- **PostgreSQL Database**: Robust data persistence with SQLAlchemy ORM
- **RESTful API**: Complete CRUD operations for all entities
- **CORS Support**: Cross-origin resource sharing for frontend integration

## 🛠️ Tech Stack

- **Framework**: FastAPI
- **Database**: PostgreSQL with SQLAlchemy ORM
- **AI Integration**: Google Gemini AI (gemini-pro)
- **Authentication**: JWT-based (ready for implementation)
- **Documentation**: Auto-generated OpenAPI/Swagger docs

## 📋 Prerequisites

- Python 3.8+
- PostgreSQL 12+
- Google Gemini AI API key

## 🔧 Installation

1. **Clone the repository and navigate to backend directory**

   ```bash
   cd backend
   ```

2. **Create a virtual environment**

   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**

   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables**

   ```bash
   cp env.example .env
   ```

   Edit `.env` file with your configuration:

   ```env
   # Database Configuration
   DATABASE_URL=postgresql://username:password@localhost:5432/airport_ops
   DATABASE_URL_ASYNC=postgresql+asyncpg://username:password@localhost:5432/airport_ops

   # Google Gemini AI Configuration
   GOOGLE_API_KEY=your_gemini_api_key_here

   # Application Settings
   SECRET_KEY=your_secret_key_here
   ALGORITHM=HS256
   ACCESS_TOKEN_EXPIRE_MINUTES=30

   # Server Configuration
   HOST=0.0.0.0
   PORT=8000
   DEBUG=True
   ```

5. **Set up PostgreSQL database**

   ```sql
   CREATE DATABASE airport_ops;
   CREATE USER airport_user WITH PASSWORD 'your_password';
   GRANT ALL PRIVILEGES ON DATABASE airport_ops TO airport_user;
   ```

6. **Seed the database with initial data**
   ```bash
   python scripts/seed_database.py
   ```

## 🚀 Running the Application

### Development Mode

```bash
python run.py
```

### Production Mode

```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

The API will be available at:

- **API**: http://localhost:8000
- **Documentation**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## 📚 API Endpoints

### Flights

- `GET /api/v1/flights/` - Get all flights with filters
- `GET /api/v1/flights/{id}` - Get specific flight
- `POST /api/v1/flights/` - Create new flight
- `PUT /api/v1/flights/{id}` - Update flight
- `DELETE /api/v1/flights/{id}` - Delete flight
- `POST /api/v1/flights/search/nlp` - Natural language flight search
- `GET /api/v1/flights/statistics/overview` - Flight statistics
- `GET /api/v1/flights/upcoming/{hours}` - Upcoming flights
- `GET /api/v1/flights/delayed/all` - Delayed flights

### Alerts

- `GET /api/v1/alerts/` - Get all alerts with filters
- `GET /api/v1/alerts/{id}` - Get specific alert
- `POST /api/v1/alerts/` - Create new alert
- `PUT /api/v1/alerts/{id}` - Update alert
- `DELETE /api/v1/alerts/{id}` - Delete alert
- `POST /api/v1/alerts/{id}/resolve` - Resolve alert
- `GET /api/v1/alerts/active/all` - Active alerts
- `GET /api/v1/alerts/critical/all` - Critical alerts
- `GET /api/v1/alerts/statistics/overview` - Alert statistics

### Runways

- `GET /api/v1/runways/` - Get runway metrics
- `GET /api/v1/runways/status/current` - Current runway status
- `GET /api/v1/runways/statistics/overview` - Runway statistics
- `GET /api/v1/runways/optimization/recommendations` - AI optimization recommendations
- `GET /api/v1/runways/{runway}/trends` - Runway utilization trends
- `GET /api/v1/runways/{runway}/peak-hours` - Peak hours analysis

### Chat

- `POST /api/v1/chat/message` - Send message to AI chatbot
- `GET /api/v1/chat/health` - Chat service health check

## 🤖 AI Features

### Natural Language Flight Search

The API uses Google Gemini AI to parse natural language queries and convert them into structured database searches.

**Example queries:**

- "Find flights to London after 3 PM tomorrow"
- "Show me British Airways flights to Dubai"
- "Next available flight to Tokyo"

### AI Chatbot

The chatbot can answer questions about:

- Flight information and searches
- Airport operations and runway status
- Real-time alerts and notifications
- General airport assistance

### Runway Optimization

AI-powered analysis of runway utilization data to provide:

- Efficiency recommendations
- Bottleneck identification
- Capacity planning suggestions
- Traffic flow optimization

## 🗄️ Database Schema

### Flights Table

- `id` (Primary Key)
- `flight_number` (String)
- `airline` (String)
- `origin` (String)
- `destination` (String)
- `departure_time` (DateTime)
- `arrival_time` (DateTime)
- `status` (Enum: On Time, Delayed, Boarding, Cancelled, Departed)
- `gate` (String)
- `terminal` (String)
- `aircraft` (String)
- `price` (Float, optional)

### Alerts Table

- `id` (Primary Key)
- `type` (Enum: critical, warning, info)
- `title` (String)
- `message` (Text)
- `timestamp` (DateTime)
- `resolved` (Boolean)

### Runway Metrics Table

- `id` (Primary Key)
- `runway` (String)
- `utilization` (Float - percentage)
- `capacity` (Integer)
- `delays` (Integer)
- `conflicts` (Integer)
- `timestamp` (DateTime)

## 🔒 Security

The API includes:

- Input validation using Pydantic schemas
- SQL injection protection via SQLAlchemy
- CORS configuration for frontend integration
- Error handling and logging
- Rate limiting ready for implementation

## 🧪 Testing

Run the tests (when implemented):

```bash
pytest
```

## 📊 Monitoring

- Health check endpoint: `GET /health`
- API documentation: `GET /docs`
- Structured logging for debugging

## 🚀 Deployment

### Docker (Recommended)

```dockerfile
FROM python:3.9-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### Environment Variables for Production

```env
DEBUG=False
DATABASE_URL=postgresql://user:pass@prod-db:5432/airport_ops
GOOGLE_API_KEY=your_production_api_key
SECRET_KEY=your_production_secret_key
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License.

## 🆘 Support

For support and questions:

- Check the API documentation at `/docs`
- Review the logs for error details
- Ensure all environment variables are properly set
- Verify database connectivity

## 🔄 Updates

To update the application:

1. Pull the latest changes
2. Update dependencies: `pip install -r requirements.txt`
3. Run database migrations if any
4. Restart the application
