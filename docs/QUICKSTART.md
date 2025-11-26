# Quick Start Guide

## Prerequisites Check
- [ ] Docker Desktop installed and running
- [ ] Git installed
- [ ] 8GB RAM available
- [ ] Ports 8000, 5432, 6379 available

## 5-Minute Setup

### Step 1: Clone & Navigate
```bash
git clone <repository-url>
cd "AI-Powered CustomerSupport & Sales Agent"
```

### Step 2: Environment Setup
```bash
# Copy environment template
cp .env.example .env

# Edit .env if needed (optional for local testing)
# Default values work for local development
```

### Step 3: Start Services
```bash
# Start all services with Docker Compose
docker-compose up -d

# Check service status
docker-compose ps
```

### Step 4: Verify Installation
```bash
# Check API health
curl http://localhost:8000/health

# Expected response:
# {"status":"healthy","environment":"development"}
```

### Step 5: Seed Test Data
```bash
# Run inside the app container
docker-compose exec app python seed_database.py
```

## Testing the Agent

### Option 1: Using API Documentation (Recommended)
1. Open browser: http://localhost:8000/docs
2. Expand `POST /webhooks/tiktok`
3. Click "Try it out"
4. Use this test payload:
```json
{
  "event_type": "message",
  "user_id": "test_user_123",
  "message": "I have a question about my order",
  "conversation_id": "test_conv_001",
  "timestamp": 1234567890
}
```
5. Click "Execute"
6. Check response

### Option 2: Using cURL
```bash
# Test support query
curl -X POST "http://localhost:8000/webhooks/tiktok" \
  -H "Content-Type: application/json" \
  -d '{
    "event_type": "message",
    "user_id": "user_123",
    "message": "My order hasn't arrived yet",
    "conversation_id": "conv_123",
    "timestamp": 1234567890
  }'

# Test sales inquiry
curl -X POST "http://localhost:8000/webhooks/linkedin" \
  -H "Content-Type: application/json" \
  -d '{
    "event_type": "message",
    "sender_id": "linkedin_user_456",
    "message_text": "What is the pricing for 50 users?",
    "conversation_id": "conv_456",
    "timestamp": 1234567890
  }'

# Test urgent message (should escalate)
curl -X POST "http://localhost:8000/webhooks/tiktok" \
  -H "Content-Type: application/json" \
  -d '{
    "event_type": "message",
    "user_id": "angry_user",
    "message": "This is ridiculous!!! I want a refund NOW!",
    "conversation_id": "conv_urgent",
    "timestamp": 1234567890
  }'
```

### Option 3: Import Postman Collection
1. Open Postman
2. Import `postman_collection.json`
3. Select any request and click "Send"

## Viewing Results

### Check Conversations
```bash
# List all conversations
curl http://localhost:8000/messages/conversations

# Get specific conversation
curl http://localhost:8000/messages/conversations/1
```

### View Analytics
```bash
# System metrics
curl http://localhost:8000/analytics/metrics

# Conversation insights
curl http://localhost:8000/analytics/conversations

# Escalation statistics
curl http://localhost:8000/analytics/escalations
```

### Check Agent Status
```bash
curl http://localhost:8000/admin/agent/status
```

## Common Operations

### View Logs
```bash
# View API logs
docker-compose logs -f app

# View specific number of lines
docker-compose logs --tail=100 app
```

### Access Database
```bash
# Connect to PostgreSQL
docker-compose exec postgres psql -U postgres -d customer_agent_db

# Sample queries:
# SELECT * FROM conversations;
# SELECT * FROM messages ORDER BY created_at DESC LIMIT 10;
```

### Stop Services
```bash
# Stop all services
docker-compose down

# Stop and remove volumes (clean slate)
docker-compose down -v
```

### Restart Services
```bash
# Restart specific service
docker-compose restart app

# Restart all services
docker-compose restart
```

## Running Tests

```bash
# Run all tests
docker-compose exec app pytest

# With coverage
docker-compose exec app pytest --cov=app tests/

# Specific test file
docker-compose exec app pytest tests/unit/test_agent_tools.py
```

## Troubleshooting

### Port Already in Use
```bash
# Check what's using the port
# Windows
netstat -ano | findstr :8000

# Change port in docker-compose.yml
ports:
  - "8080:8000"  # Use 8080 instead
```

### Database Connection Error
```bash
# Check if PostgreSQL is running
docker-compose ps postgres

# Restart PostgreSQL
docker-compose restart postgres
```

### Agent Not Responding
```bash
# Check logs for errors
docker-compose logs app

# Restart application
docker-compose restart app
```

## Next Steps

1. ✅ **Explore API**: Visit http://localhost:8000/docs
2. ✅ **Test Scenarios**: Try different message types
3. ✅ **View Analytics**: Check metrics and insights
4. ✅ **Read Documentation**: See `docs/ARCHITECTURE.md`
5. ✅ **Enable LLM**: Add API keys to `.env` for real AI responses

## Production Deployment

For production deployment, see:
- [README.md](README.md) - Deployment section
- [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) - Architecture details

## Support

- API Documentation: http://localhost:8000/docs
- View Logs: `docker-compose logs -f`
- Check Status: `curl http://localhost:8000/health`

---

**You're all set!** 🎉 The AI agent is ready to handle customer messages.
