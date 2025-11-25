# AI-Powered Customer Support & Sales Agent

[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.109.0-green.svg)](https://fastapi.tiangolo.com/)
[![LangGraph](https://img.shields.io/badge/LangGraph-Latest-orange.svg)](https://github.com/langchain-ai/langgraph)

An intelligent customer support and sales agent that automates responses across **TikTok** and **LinkedIn** messaging platforms using **FastAPI** and **LangGraph**.

## 🎯 Features

### Core Capabilities
- 🤖 **Multi-Intent Recognition**: Automatically classifies messages as support, sales, general, or urgent
- 💬 **Context-Aware Responses**: Maintains conversation history for coherent interactions
- 🚨 **Smart Escalation**: Detects urgent issues and escalates to human agents
- 📊 **Analytics Dashboard**: Track metrics, response times, and sentiment
- 🔌 **Multi-Platform Support**: TikTok and LinkedIn integrations
- ⚡ **Async Processing**: Redis-based message queue for scalability

### Agent Workflow (LangGraph)
1. **Message Classification**: Determine intent and urgency
2. **Context Retrieval**: Load conversation history
3. **Escalation Check**: Identify critical issues
4. **Response Generation**: Create appropriate responses
5. **Validation**: Ensure response quality

## 📁 Project Structure

```
project/
├── app/
│   ├── agent/              # LangGraph agent implementation
│   │   ├── graph.py        # Workflow definition
│   │   ├── nodes.py        # Agent nodes
│   │   ├── prompts.py      # System prompts
│   │   └── tools.py        # Utility functions
│   ├── api/                # FastAPI routes
│   │   └── routes/
│   │       ├── webhooks.py # Platform webhook handlers
│   │       ├── messages.py # Message endpoints
│   │       ├── analytics.py # Analytics endpoints
│   │       └── admin.py    # Admin endpoints
│   ├── integrations/       # Platform clients
│   │   ├── tiktok.py       # TikTok API client (mock)
│   │   └── linkedin.py     # LinkedIn API client (mock)
│   ├── models/             # Database models
│   │   ├── database.py     # SQLAlchemy models
│   │   └── schemas.py      # Pydantic schemas
│   ├── services/           # Business logic
│   │   ├── message_processor.py
│   │   ├── conversation.py
│   │   └── analytics.py
│   ├── utils/              # Utilities
│   │   ├── logger.py       # Logging configuration
│   │   └── exceptions.py   # Custom exceptions
│   ├── config.py           # Configuration
│   └── main.py             # FastAPI application
├── tests/                  # Tests
│   ├── unit/               # Unit tests
│   └── integration/        # Integration tests
├── alembic/                # Database migrations
├── docker-compose.yml      # Docker services
├── Dockerfile              # Application Dockerfile
├── requirements.txt        # Python dependencies
├── .env.example            # Environment template
└── README.md
```

## 🚀 Quick Start

### Prerequisites
- Python 3.11+
- Docker & Docker Compose
- PostgreSQL (via Docker)
- Redis (via Docker)

### Installation

#### 1. Clone and Setup
```bash
git clone <repository-url>
cd AI-Powered\ CustomerSupport\ &\ Sales\ Agent
```

#### 2. Environment Configuration
```bash
cp .env.example .env
```

Edit `.env` and configure:
- Database credentials
- LLM API keys (OpenAI or Anthropic - optional, will use mock if not provided)
- Platform credentials (TikTok, LinkedIn - optional for development)

#### 3. Docker Setup (Recommended)
```bash
# Start all services
docker-compose up -d

# Check logs
docker-compose logs -f app
```

The API will be available at `http://localhost:8000`

#### 4. Local Setup (Alternative)
```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Start PostgreSQL and Redis (must be running)
# Then run the application
uvicorn app.main:app --reload
```

### 5. Database Migrations
```bash
# Initialize Alembic (first time only)
alembic revision --autogenerate -m "Initial migration"

# Run migrations
alembic upgrade head
```

## 📚 API Documentation

Once the application is running, visit:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

### Key Endpoints

#### Webhooks
- `POST /webhooks/tiktok` - Receive TikTok messages
- `POST /webhooks/linkedin` - Receive LinkedIn messages
- `GET /webhooks/verify` - Webhook verification

#### Messages
- `POST /messages/send` - Send message to platform
- `GET /messages/conversations` - List all conversations
- `GET /messages/conversations/{id}` - Get conversation details

#### Analytics
- `GET /analytics/metrics` - System metrics (response time, escalation rate, etc.)
- `GET /analytics/conversations` - Conversation insights by intent
- `GET /analytics/escalations` - Escalation statistics

#### Admin
- `POST /admin/escalate/{conversation_id}` - Manually escalate conversation
- `PUT /admin/override/{message_id}` - Override AI response
- `GET /admin/logs` - View system logs
- `POST /admin/agent/configure` - Update agent configuration
- `GET /admin/agent/status` - Get agent health status

## 🧪 Testing

### Run All Tests
```bash
# With coverage
pytest --cov=app tests/

# Specific test file
pytest tests/unit/test_agent_tools.py

# Integration tests only
pytest tests/integration/
```

### Test Coverage
```bash
pytest --cov=app --cov-report=html tests/
# View coverage report at htmlcov/index.html
```

## 🔧 Configuration

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `DATABASE_URL` | PostgreSQL connection string | `postgresql://postgres:postgres@localhost:5432/customer_agent_db` |
| `REDIS_URL` | Redis connection string | `redis://localhost:6379/0` |
| `LLM_PROVIDER` | LLM provider (`openai`, `anthropic`, `mock`) | `mock` |
| `OPENAI_API_KEY` | OpenAI API key (optional) | `None` |
| `ANTHROPIC_API_KEY` | Anthropic API key (optional) | `None` |
| `AGENT_MAX_TOKENS` | Max tokens for LLM responses | `500` |
| `AGENT_TEMPERATURE` | LLM temperature | `0.7` |
| `LOG_LEVEL` | Logging level | `INFO` |

## 🎨 Agent Behavior Examples

### Scenario 1: Customer Support (TikTok)
**User**: "Hey, I ordered the blue hoodie 3 days ago but haven't received tracking info yet"

**Agent**:
- Classifies as `SUPPORT`
- Detects no urgency
- Responds: "Thank you for reaching out! I understand your concern. Could you please provide your order number so I can look into this for you right away?"

### Scenario 2: Sales Inquiry (LinkedIn)
**User**: "I'm interested in your enterprise plan. What's the pricing for 50 users?"

**Agent**:
- Classifies as `SALES`
- Generates persuasive response
- Captures lead information

### Scenario 3: Urgent Escalation
**User**: "This is ridiculous! I've been charged twice and no one is helping me!"

**Agent**:
- Classifies as `URGENT`
- **Immediately escalates** to human agent
- Flags as high priority
- Sends empathetic escalation message

## 🏗️ Architecture

### System Components

```mermaid
graph TB
    A[TikTok/LinkedIn] -->|Webhook| B[FastAPI]
    B --> C[Message Processor]
    C --> D[LangGraph Agent]
    D --> E[Intent Classifier]
    E --> F[Response Generator]
    F --> G[Escalation Checker]
    G --> H[Response Validator]
    H --> I[Database]
    H --> J[Platform API]
    C --> K[Redis Queue]
    K --> L[Celery Worker]
    I --> M[Analytics Service]
```

### Database Schema

**Users** → **Conversations** → **Messages**

- **Users**: Platform-specific user profiles
- **Conversations**: Conversation threads with status tracking
- **Messages**: Individual messages with sentiment and intent
- **AgentConfig**: Agent configuration and prompts
- **Analytics**: System metrics and insights

## 🔐 Security Notes

- All API endpoints should be secured with authentication in production
- Webhook signatures should be verified (implemented in platform clients)
- Environment variables should be properly secured
- Database connections use connection pooling
- Rate limiting implemented for platform APIs

## 📊 Monitoring & Logging

### Logs Location
- **Console**: Colored output with loguru
- **File**: `logs/app.log` (rotated at 500MB, 10 days retention)

### Log Levels
```bash
# Change log level in .env
LOG_LEVEL=DEBUG  # DEBUG, INFO, WARNING, ERROR, CRITICAL
```

## 🚢 Deployment

### Docker Production Build
```bash
docker build -t customer-agent:latest .
docker-compose -f docker-compose.yml up -d
```

### Environment Checklist
- [ ] Set secure database password
- [ ] Configure LLM API keys
- [ ] Set up platform OAuth credentials
- [ ] Configure backup strategy
- [ ] Set up monitoring (Prometheus/Grafana)
- [ ] Configure reverse proxy (Nginx)

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📝 License

This project is part of a software engineering evaluation task for FlowGenX.ai

## 🛠️ Development

### Code Quality
```bash
# Type checking
mypy app/

# Linting (if configured)
flake8 app/
```

### Adding New Intents
1. Update `MessageIntent` enum in `models/database.py`
2. Add prompt in `agent/prompts.py`
3. Update classification logic in `agent/nodes.py`
4. Add tests

## 📞 Support

For questions or issues:
- Check the API documentation at `/docs`
- Review logs at `/admin/logs`
- Check agent status at `/admin/agent/status`

---

**Built with** ❤️ **using FastAPI, LangGraph, and LangChain**
