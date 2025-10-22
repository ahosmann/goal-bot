# GoalBot Setup Guide

## 🚀 Quick Setup (5 minutes)

### Step 1: Install Dependencies

```bash
cd backend
pip install -r requirements.txt
```

**New dependencies added for GoalBot:**
- `sqlalchemy>=2.0.0` - Database ORM
- `psycopg2-binary>=2.9.0` - PostgreSQL driver
- `passlib[bcrypt]>=1.7.4` - Password hashing
- `python-jose[cryptography]>=3.3.0` - JWT tokens
- `python-dateutil>=2.8.2` - Date utilities

### Step 2: Configure Environment

Copy the example and edit with your API keys:
```bash
cp backend/.env.example backend/.env
```

**Minimum required in `.env`:**
```bash
OPENAI_API_KEY=sk-your-key-here
```

**Optional but recommended:**
```bash
DATABASE_URL=sqlite:///./goalbot.db
JWT_SECRET_KEY=your-random-secret-key
```

### Step 3: Start the Server

```bash
# From project root
./start.sh

# The server will automatically:
# - Initialize the SQLite database
# - Create all tables (users, goals, daily_check_ins)
# - Register GoalBot routes at /api/goalbot
```

### Step 4: Test the API

```bash
# Run comprehensive test suite
python "test scripts/test_goalbot.py"
```

Expected output:
```
🚀 GoalBot API Test Suite
============================================================
🔐 Testing Signup...
✓ Signup successful!
🔐 Testing Login...
✓ Login successful!
🎯 Testing Goal Creation...
✓ Goal created!
...
✅ All tests completed successfully!
```

### Step 5: Use the Frontend

Open in browser:
- **GoalBot Chat UI**: http://localhost:8000/frontend/goalbot.html
- **API Documentation**: http://localhost:8000/docs

## 📁 What Was Built

### Backend Files (7 new files)

1. **`backend/database.py`**
   - SQLAlchemy configuration
   - Session management
   - Database initialization

2. **`backend/models.py`**
   - User model (authentication)
   - Goal model (30-day goals)
   - DailyCheckIn model (progress tracking)

3. **`backend/auth.py`**
   - JWT token creation/validation
   - Password hashing (bcrypt)
   - Authentication middleware

4. **`backend/schemas.py`**
   - Pydantic models for API requests/responses
   - Input validation
   - Type safety

5. **`backend/goalbot_agents.py`**
   - 4 AI agents (Clarification, Refinement, Breakdown, Check-in)
   - LangGraph workflow
   - GoalState management

6. **`backend/goalbot.py`**
   - 12 API endpoints
   - Authentication routes
   - Goal management routes
   - Check-in routes

7. **`backend/data/goal_templates.json`**
   - Goal templates for 7 categories
   - Best practices and success tips
   - Common obstacles and solutions

### Frontend Files (1 new file)

8. **`frontend/goalbot.html`**
   - Modern chat interface
   - User authentication UI
   - Progress tracking visualization
   - Conversational goal setup

### Test Files (1 new file)

9. **`test scripts/test_goalbot.py`**
   - Comprehensive API test suite
   - Tests all endpoints
   - Complete workflow validation

### Documentation (3 new files)

10. **`my_agent_prd.md`** - Product Requirements Document
11. **`GOALBOT_README.md`** - Complete documentation
12. **`GOALBOT_SETUP.md`** - This file!

## 🔍 Verify Installation

### Check Database

```bash
# After first run, you should see:
ls backend/goalbot.db  # SQLite database file exists
```

### Check Routes

```bash
# Visit API docs
open http://localhost:8000/docs

# You should see new routes:
# - /api/goalbot/signup
# - /api/goalbot/login
# - /api/goalbot/goals/*
```

### Check Frontend

```bash
# Visit GoalBot UI
open http://localhost:8000/frontend/goalbot.html

# You should see:
# - Purple gradient design
# - Login/Signup forms
# - "GoalBot" header
```

## 🧪 Manual Testing

### Test 1: Create Account
```bash
curl -X POST http://localhost:8000/api/goalbot/signup \
  -H "Content-Type: application/json" \
  -d '{
    "username": "testuser",
    "email": "test@example.com",
    "password": "password123"
  }'
```

Expected: `{"access_token": "eyJ...", "token_type": "bearer"}`

### Test 2: Create Goal
```bash
# Save token from previous step
TOKEN="your-token-here"

curl -X POST http://localhost:8000/api/goalbot/goals/create \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"goal": "Learn Python programming"}'
```

Expected: Goal ID + clarification questions

### Test 3: Check Health
```bash
curl http://localhost:8000/health
```

Expected: `{"status": "healthy", "service": "ai-trip-planner"}`

## 🐛 Troubleshooting

### Error: "No module named 'sqlalchemy'"
```bash
# Install missing dependencies
cd backend
pip install -r requirements.txt
```

### Error: "Could not validate credentials"
```bash
# Token might be expired (7-day expiry)
# Login again to get a new token
```

### Error: "OPENAI_API_KEY not set"
```bash
# Check .env file exists
ls backend/.env

# Verify key is set
grep OPENAI_API_KEY backend/.env
```

### Database Reset
```bash
# If you need to start fresh
rm backend/goalbot.db
# Restart server to recreate
```

## 📊 Database Schema

The system creates 3 tables automatically:

**users**
- id, email, username, hashed_password
- created_at, is_active

**goals**
- id, user_id, original_goal, refined_goal
- clarification_qa, daily_tasks, milestones
- current_day, status (clarifying/active/completed)
- created_at, started_at, completed_at

**daily_check_ins**
- id, goal_id, day_number (1-30)
- task_completed, user_response, obstacles
- confidence_level, agent_feedback
- checked_in_at

## 🎯 Next Steps

1. **Try the UI**: Create an account at http://localhost:8000/frontend/goalbot.html
2. **Set a Real Goal**: Use the conversational interface
3. **Track Progress**: Complete daily check-ins
4. **Explore API**: Check out http://localhost:8000/docs
5. **Customize Agents**: Edit prompts in `backend/goalbot_agents.py`

## 🔐 Security Notes

**Development Setup:**
- Using SQLite (fine for local development)
- JWT tokens stored in localStorage (acceptable for MVP)
- Default JWT secret (change in production!)

**Production Checklist:**
- [ ] Use PostgreSQL instead of SQLite
- [ ] Set strong JWT_SECRET_KEY
- [ ] Enable HTTPS only
- [ ] Add rate limiting
- [ ] Set up proper CORS origins
- [ ] Use secure cookie storage for tokens
- [ ] Add refresh token mechanism

## 📈 Success Metrics

Track these to measure GoalBot effectiveness:

1. **Goal Completion Rate**: % of goals reaching day 30
2. **Daily Check-In Adherence**: % of expected check-ins completed
3. **Average Time to Refinement**: How long clarification takes
4. **Second Sprint Rate**: % of users starting another 30-day goal

Access these via:
```bash
# Progress endpoint
curl http://localhost:8000/api/goalbot/goals/{goal_id}/progress \
  -H "Authorization: Bearer $TOKEN"
```

## 🎓 Learning Resources

- **LangGraph Tutorial**: https://langchain-ai.github.io/langgraph/
- **FastAPI Docs**: https://fastapi.tiangolo.com/
- **SQLAlchemy ORM**: https://docs.sqlalchemy.org/
- **JWT Authentication**: https://jwt.io/introduction

---

**Questions or Issues?**
Check `GOALBOT_README.md` for detailed documentation or review the PRD in `my_agent_prd.md`.

