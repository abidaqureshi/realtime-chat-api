# Real-Time Chat API

A high-performance, real-time chat application built with **FastAPI**, **WebSockets**, **PostgreSQL**, **Redis**, and **Celery**. Features include real-time messaging, JWT authentication, online status tracking, message persistence, and read receipts.

## 🚀 Features

- **Real-time Messaging**: WebSocket-based instant message delivery
- **JWT Authentication**: Secure token-based authentication
- **Online Status Tracking**: Real-time user presence indicators
- **Message Read Receipts**: Track when messages are read
- **Message Persistence**: PostgreSQL database for message history
- **Rate Limiting**: Redis-based API rate limiting
- **Background Processing**: Celery for async tasks (notifications, analytics)
- **RESTful API**: Clean API endpoints for chat operations
- **WebSocket Events**: Real-time bidirectional communication

## 🛠 Tech Stack

### Backend
- **FastAPI** - Modern Python web framework
- **SQLAlchemy** - Async ORM for database operations
- **PostgreSQL** - Primary database for data persistence
- **Redis** - Real-time status tracking and rate limiting
- **Celery** - Background task processing
- **JWT** - JSON Web Tokens for authentication
- **WebSockets** - Real-time bidirectional communication
- **Uvicorn** - ASGI server

### Frontend ([React Chat frontend](https://github.com/abidaqureshi/realtime-chat-frontend))
- **React** + **TypeScript** - Frontend framework
- **Tailwind CSS** - Utility-first CSS framework
- **Vite** - Fast build tool and dev server
- **Axios** - HTTP client for API calls
- **WebSocket API** - Native browser WebSocket client

## 📋 Prerequisites

- Python 3.8+
- PostgreSQL 13+
- Redis 6+


## 🔧 Installation

### 1. Clone the Repository
```bash
git clone <repository-url>
cd RealTimeChatAPI
```

### 2. Backend Setup

#### Create Virtual Environment
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

#### Install Dependencies
```bash
pip install -r requirements.txt
```

#### Environment Configuration
Create `.env` file:
```env
# Database
DATABASE_URL=postgresql+asyncpg://username:password@localhost/chat_db

# JWT
SECRET_KEY=your-super-secret-key-here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Redis
REDIS_URL=redis://localhost:6379

# Celery
CELERY_BROKER_URL=redis://localhost:6379/0
CELERY_RESULT_BACKEND=redis://localhost:6379/0

# Optional: Email (for notifications)
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your-email@gmail.com
SMTP_PASSWORD=your-app-password
SMTP_FROM_EMAIL=noreply@yourapp.com
```

#### Database Setup
```bash
# Create database (PostgreSQL)
createdb chat_db

# Run migrations (if using Alembic)
alembic upgrade head

# Or create tables automatically (development)
python -c "from app.main import app; from app.models.base import Base; from app.core.database import engine; Base.metadata.create_all(bind=engine)"
```

### 3. Frontend Setup (Optional)

```bash
cd chat-frontend
npm install

# Create Tailwind config (if needed)
npx tailwindcss init -p
```

## 🚀 Running the Application

### Start Required Services

#### Terminal 1: Redis
```bash
redis-server
```

#### Terminal 2: PostgreSQL
```bash
# Ensure PostgreSQL is running
pg_ctl start  # Or use your system's service manager
```

#### Terminal 3: FastAPI Backend
```bash
source venv/bin/activate
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

#### Terminal 4: Celery Worker
```bash
source venv/bin/activate
celery -A app.celery_app worker --loglevel=info
```

#### Terminal 5: Frontend (Optional)
```bash
cd chat-frontend
npm run dev
```

### Access Points
- **API Documentation**: http://localhost:8000/docs
- **Frontend Application**: http://localhost:3000
- **Celery Monitoring** (Flower): http://localhost:5555 (if enabled)

## 📚 API Documentation

### Authentication Endpoints

#### Register User
```http
POST /api/v1/auth/register
Content-Type: application/json

{
  "username": "john_doe",
  "email": "john@example.com",
  "password": "securepassword123"
}
```

#### Login
```http
POST /api/v1/auth/login
Content-Type: application/x-www-form-urlencoded

username=john_doe&password=securepassword123
```

### Chat Endpoints

#### Get Conversation History
```http
GET /api/v1/chat/conversation/{username}
Authorization: Bearer <jwt_token>
```

#### Mark Message as Read
```http
POST /api/v1/chat/messages/read/{message_uuid}
Authorization: Bearer <jwt_token>
```

### WebSocket Connection
```javascript
// Connect to WebSocket
const ws = new WebSocket(`ws://localhost:8000/api/v1/chat/ws/${jwt_token}`);

// Send message
ws.send(JSON.stringify({
  type: "message",
  data: {
    content: "Hello!",
    receiver: "other_user"
  }
}));

// Mark as read
ws.send(JSON.stringify({
  type: "read_receipt", 
  data: {
    message_uuid: "message-uuid-here"
  }
}));
```

## 🔌 WebSocket Events

### Client → Server
```typescript
// Send message
{
  type: "message",
  data: {
    content: string,
    receiver: string
  }
}

// Mark as read
{
  type: "read_receipt", 
  data: {
    message_uuid: string
  }
}
```

### Server → Client
```typescript
// New message
{
  type: "new_message",
  data: MessageResponse
}

// Message read receipt
{
  type: "message_read",
  data: {
    message_uuid: string,
    read_at: string
  }
}

// User status change
{
  type: "user_status", 
  data: {
    user_id: string,
    status: "online" | "offline"
  }
}
```

## 🗄 Database Schema

### Users Table
```sql
id | uuid | username | email | hashed_password | is_online | last_seen | created_at | updated_at
```

### Messages Table
```sql
id | uuid | content | sender_id | receiver_id | is_read | read_at | created_at | updated_at
```

## 🔒 Security Features

- **JWT Authentication** with expiration
- **Password Hashing** using bcrypt
- **Rate Limiting** with Redis sliding window
- **CORS Protection** configured
- **Input Validation** with Pydantic schemas
- **SQL Injection Protection** with SQLAlchemy

## 🧪 Testing

### Run Tests
```bash
pytest tests/ -v
```

### Test WebSocket Connection
```python
import websockets
import json
import asyncio

async def test_websocket():
    async with websockets.connect("ws://localhost:8000/api/v1/chat/ws/your-jwt-token") as ws:
        # Send test message
        await ws.send(json.dumps({
            "type": "message",
            "data": {
                "content": "Test message",
                "receiver": "test_user"
            }
        }))
        
        # Receive response
        response = await ws.recv()
        print(response)

asyncio.run(test_websocket())
```

## 📊 Monitoring

### Celery Task Monitoring
```bash
# Install Flower
pip install flower

# Start monitoring
celery -A app.celery_app flower --port=5555
```

### Redis Monitoring
```bash
redis-cli monitor
```

## 🚢 Deployment

### Docker Compose (Recommended)
```yaml
# docker-compose.yml
version: '3.8'
services:
  postgres:
    image: postgres:13
    environment:
      POSTGRES_DB: chat_db
      POSTGRES_USER: user
      POSTGRES_PASSWORD: password
    volumes:
      - postgres_data:/var/lib/postgresql/data

  redis:
    image: redis:6-alpine

  backend:
    build: .
    command: uvicorn app.main:app --host 0.0.0.0 --port 8000
    environment:
      - DATABASE_URL=postgresql+asyncpg://user:password@postgres/chat_db
      - REDIS_URL=redis://redis:6379
    depends_on:
      - postgres
      - redis

  celery:
    build: .
    command: celery -A app.celery_app worker --loglevel=info
    environment:
      - DATABASE_URL=postgresql+asyncpg://user:password@postgres/chat_db
      - REDIS_URL=redis://redis:6379
    depends_on:
      - postgres
      - redis

volumes:
  postgres_data:
```

### Environment Variables for Production
```env
DEBUG=false
SECRET_KEY=your-production-secret-key
ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🆘 Troubleshooting

### Common Issues

1. **WebSocket Connection Failed**
   - Check if JWT token is valid and not expired
   - Verify Redis is running
   - Check CORS settings

2. **Celery Tasks Not Executing**
   - Ensure Redis is running and accessible
   - Check Celery worker logs for errors
   - Verify task imports in celery_app.py

3. **Database Connection Issues**
   - Verify PostgreSQL is running
   - Check DATABASE_URL in .env file
   - Ensure database exists and user has permissions

4. **Rate Limiting Too Aggressive**
   - Adjust rate limit settings in dependencies.py
   - Check Redis for accumulated requests

### Getting Help
- Check the [API Documentation](http://localhost:8000/docs)
- Review application logs
- Check Redis and PostgreSQL connection status

## 🙏 Acknowledgments

- FastAPI for the excellent web framework
- SQLAlchemy for robust ORM support
- Redis for real-time capabilities
- Celery for background task processing
- React community for frontend tools

---

**Happy Coding!** 🎉
