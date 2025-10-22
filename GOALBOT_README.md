# GoalBot - 30-Day Goal Achievement System

GoalBot is an AI-powered goal achievement agent built on top of the AI Trip Planner architecture. It helps users transform vague goals into achievable 30-day sprints through intelligent clarification, SMART goal refinement, daily task breakdown, and personalized check-ins.

## 🎯 What is GoalBot?

GoalBot specializes in:
- **Goal Clarification**: Asks targeted questions to understand your context, motivation, and resources
- **30-Day Scoping**: Refines ambitious goals into achievable 30-day milestones
- **Daily Breakdown**: Creates 30 daily tasks with clear success criteria
- **Daily Check-Ins**: Provides encouragement, tracks progress, and adjusts plans when needed

## 🏗️ Architecture

### Multi-Agent System (LangGraph)
```
User Goal Input
     ↓
Clarification Agent → Refinement Agent → Breakdown Agent
     ↓                      ↓                  ↓
 Questions          SMART Goal         30 Daily Tasks
                                             ↓
                                      Check-In Agent
                                      (Daily Feedback)
```

### Tech Stack
- **Backend**: FastAPI with SQLAlchemy
- **AI Agents**: LangGraph + LangChain
- **LLM**: OpenAI GPT (configurable)
- **Database**: SQLite (dev) / PostgreSQL (production)
- **Authentication**: JWT tokens with bcrypt
- **Frontend**: Vanilla JS with modern UI

## 🚀 Quick Start

### 1. Install Dependencies

```bash
cd backend
pip install -r requirements.txt
```

### 2. Configure Environment

Create `backend/.env`:
```bash
# Required: LLM Provider
OPENAI_API_KEY=your_openai_api_key_here

# Optional: Database (defaults to SQLite)
DATABASE_URL=sqlite:///./goalbot.db
# For PostgreSQL: DATABASE_URL=postgresql://user:pass@localhost/goalbot

# Optional: JWT Secret (generates default if not set)
JWT_SECRET_KEY=your-secret-key-here

# Optional: Observability
ARIZE_SPACE_ID=your_arize_space_id
ARIZE_API_KEY=your_arize_api_key
```

### 3. Run the Server

```bash
# From project root
./start.sh

# Or directly
cd backend
uvicorn main:app --reload --port 8000
```

The server will:
- Initialize the database automatically
- Register GoalBot routes at `/api/goalbot`
- Serve the frontend at `http://localhost:8000`

### 4. Access the UI

- **GoalBot Interface**: `http://localhost:8000/frontend/goalbot.html`
- **API Documentation**: `http://localhost:8000/docs`
- **Health Check**: `http://localhost:8000/health`

## 📡 API Endpoints

### Authentication
- `POST /api/goalbot/signup` - Create account
- `POST /api/goalbot/login` - Login and get JWT token
- `GET /api/goalbot/me` - Get current user info

### Goal Management
- `POST /api/goalbot/goals/create` - Create goal and get clarification questions
- `POST /api/goalbot/goals/{id}/clarify` - Submit clarification answers
- `POST /api/goalbot/goals/{id}/breakdown` - Generate 30-day breakdown
- `GET /api/goalbot/goals` - List all goals
- `GET /api/goalbot/goals/{id}` - Get goal details
- `GET /api/goalbot/goals/{id}/progress` - Get progress summary

### Daily Check-Ins
- `POST /api/goalbot/goals/{id}/check-in` - Submit daily check-in
- `GET /api/goalbot/goals/{id}/check-ins` - Get all check-ins

## 🧪 Testing

```bash
# Run test suite
python "test scripts/test_goalbot.py"

# Or test individual endpoints
curl -X POST http://localhost:8000/api/goalbot/signup \
  -H "Content-Type: application/json" \
  -d '{"username":"testuser","email":"test@example.com","password":"password123"}'
```

## 📊 Database Schema

### Users
- id, email, username, hashed_password
- created_at, is_active

### Goals
- id, user_id, original_goal, refined_goal
- clarification_qa, daily_tasks, milestones
- current_day, status, completed

### DailyCheckIns
- id, goal_id, day_number
- task_completed, user_response, obstacles
- confidence_level, agent_feedback

## 🎨 Frontend Features

The GoalBot UI (`frontend/goalbot.html`) provides:
- ✅ User authentication (signup/login)
- ✅ Conversational goal setup
- ✅ Progress tracking with visual indicators
- ✅ Daily check-in interface
- 🚧 Milestone celebrations (coming soon)
- 🚧 Goal history and analytics (coming soon)

## 🔧 Development

### Project Structure
```
backend/
├── main.py              # FastAPI app (includes trip planner)
├── goalbot.py           # GoalBot API routes
├── goalbot_agents.py    # AI agents and LangGraph workflow
├── models.py            # SQLAlchemy database models
├── schemas.py           # Pydantic request/response schemas
├── auth.py              # JWT authentication utilities
├── database.py          # Database configuration
└── data/
    └── goal_templates.json  # Goal templates by category

frontend/
├── index.html           # Trip planner UI
└── goalbot.html         # GoalBot chat interface

test scripts/
└── test_goalbot.py      # Comprehensive test suite
```

### Adding New Features

1. **New Agent**: Add function in `goalbot_agents.py` and update workflow
2. **New Endpoint**: Add route in `goalbot.py` with proper authentication
3. **New Goal Category**: Add template to `data/goal_templates.json`

## 🎯 Usage Example

### 1. Create Account
```python
import requests

response = requests.post('http://localhost:8000/api/goalbot/signup', json={
    'username': 'john_doe',
    'email': 'john@example.com',
    'password': 'secure_password'
})
token = response.json()['access_token']
```

### 2. Create Goal
```python
response = requests.post(
    'http://localhost:8000/api/goalbot/goals/create',
    headers={'Authorization': f'Bearer {token}'},
    json={'goal': 'Learn Spanish for travel'}
)
goal_data = response.json()
```

### 3. Answer Clarification Questions
```python
answers = {
    'q1': 'I know zero Spanish currently',
    'q2': 'I want to have basic conversations in 30 days',
    'q3': 'Traveling to Spain in 2 months',
    'q4': 'Can practice 30 minutes daily'
}

response = requests.post(
    f'http://localhost:8000/api/goalbot/goals/{goal_id}/clarify',
    headers={'Authorization': f'Bearer {token}'},
    json={'answers': answers}
)
```

### 4. Get Daily Tasks
```python
response = requests.post(
    f'http://localhost:8000/api/goalbot/goals/{goal_id}/breakdown',
    headers={'Authorization': f'Bearer {token}'}
)
breakdown = response.json()
print(f"Day 1: {breakdown['daily_tasks'][0]['task']}")
```

### 5. Daily Check-In
```python
response = requests.post(
    f'http://localhost:8000/api/goalbot/goals/{goal_id}/check-in',
    headers={'Authorization': f'Bearer {token}'},
    json={
        'task_completed': True,
        'user_response': 'Completed 30 min Duolingo lesson',
        'obstacles': None,
        'confidence_level': 4
    }
)
feedback = response.json()['agent_feedback']
```

## 🌟 Key Differentiators

1. **Active Refinement**: Unlike passive trackers, GoalBot helps you scope goals appropriately
2. **30-Day Sprints**: Focus on achievable milestones, not overwhelming long-term commitments
3. **AI-Powered Check-Ins**: Contextual feedback based on your progress patterns
4. **Adaptive Planning**: Adjusts remaining tasks when you fall behind

## 📈 Success Metrics (PRD Goals)

- **Primary**: 70%+ goal completion rate, 75%+ daily check-in adherence
- **Secondary**: <5 min goal refinement time, 50%+ second sprint retention
- **Qualitative**: User satisfaction scores, task quality reviews

## 🔮 Roadmap

### Phase 1 (Current - MVP)
- ✅ Goal clarification, refinement, breakdown
- ✅ User authentication and state persistence
- ✅ Basic check-in system

### Phase 2 (Next)
- 🚧 Scheduled daily notifications
- 🚧 Progress dashboard with analytics
- 🚧 Adaptive replanning based on patterns

### Phase 3 (Future)
- 🔮 RAG system with success patterns
- 🔮 Community features and accountability partners
- 🔮 Mobile app
- 🔮 Integration with habit trackers

## 🤝 Contributing

This is a learning project built on the AI Trip Planner architecture. Feel free to:
- Experiment with different agent prompts
- Add new goal categories and templates
- Improve the UI/UX
- Enhance the check-in agent's intelligence

## 📝 License

Same as AI Trip Planner - built for educational purposes.

## 🆘 Troubleshooting

### Database Issues
```bash
# Reset database
rm backend/goalbot.db
# Restart server to recreate
```

### Authentication Errors
- Ensure JWT_SECRET_KEY is set consistently
- Check token is being passed in Authorization header
- Tokens expire after 7 days by default

### Agent Not Working
- Verify OPENAI_API_KEY is set
- Check API quota/limits
- Review server logs for detailed errors

## 📚 Learn More

- **Architecture**: See `IMPLEMENTATION_SPEC.md` for trip planner patterns
- **PRD**: Read `my_agent_prd.md` for product requirements
- **API Docs**: Visit `http://localhost:8000/docs` when server is running

---

**Built with ❤️ on the AI Trip Planner architecture**

