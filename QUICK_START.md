# 🎯 GoalBot - Quick Start

## What Is This?

**GoalBot** is a fully functional AI-powered goal achievement system that helps users reach their goals in 30-day sprints. It was built based on the PRD in `my_agent_prd.md`.

## ⚡ 3-Minute Quick Start

### 1. Install & Run
```bash
# Install dependencies
cd backend
pip install -r requirements.txt

# Create .env file
echo "OPENAI_API_KEY=your-key-here" > .env

# Start server
cd ..
./start.sh
```

### 2. Test It Works
```bash
# Run test suite
python "test scripts/test_goalbot.py"
```

### 3. Use the Interface
```bash
# Open in browser
open http://localhost:8000/frontend/goalbot.html

# Or use API docs
open http://localhost:8000/docs
```

## 📁 What Was Built

### ✅ Complete System (12 New Files)

**Backend (7 files)**
1. `backend/database.py` - Database setup
2. `backend/models.py` - User, Goal, CheckIn models
3. `backend/auth.py` - JWT authentication
4. `backend/schemas.py` - API schemas
5. `backend/goalbot_agents.py` - 4 AI agents
6. `backend/goalbot.py` - 11 API endpoints
7. `backend/data/goal_templates.json` - Goal templates

**Frontend (1 file)**
8. `frontend/goalbot.html` - Chat interface

**Tests (1 file)**
9. `test scripts/test_goalbot.py` - Test suite

**Documentation (3 files)**
10. `my_agent_prd.md` - Product Requirements
11. `GOALBOT_README.md` - Complete docs
12. `GOALBOT_SETUP.md` - Setup guide

## 🎨 Features

### ✅ User Authentication
- Signup with email/username/password
- Login with JWT tokens
- Secure password hashing

### ✅ 4 AI Agents (LangGraph)
1. **Clarification Agent** - Asks 3-5 questions about your goal
2. **Refinement Agent** - Creates SMART 30-day goal
3. **Breakdown Agent** - Generates 30 daily tasks
4. **Check-In Agent** - Daily feedback & encouragement

### ✅ 11 API Endpoints
- POST `/api/goalbot/signup` - Create account
- POST `/api/goalbot/login` - Login
- GET `/api/goalbot/me` - Get user info
- POST `/api/goalbot/goals/create` - Start goal
- POST `/api/goalbot/goals/{id}/clarify` - Submit answers
- POST `/api/goalbot/goals/{id}/breakdown` - Get tasks
- GET `/api/goalbot/goals` - List goals
- GET `/api/goalbot/goals/{id}` - Goal details
- GET `/api/goalbot/goals/{id}/progress` - Progress summary
- POST `/api/goalbot/goals/{id}/check-in` - Daily check-in
- GET `/api/goalbot/goals/{id}/check-ins` - Check-in history

### ✅ Modern UI
- Beautiful purple gradient design
- Conversational goal setup
- Progress visualization
- Daily check-in interface

## 🔄 User Flow

```
1. Sign Up
   ↓
2. Enter Goal: "I want to learn Python"
   ↓
3. Answer Questions:
   - Current state?
   - What does success look like?
   - Why is this important?
   - How much time daily?
   ↓
4. Get Refined Goal:
   "Complete Python fundamentals and build 3 projects in 30 days"
   ↓
5. Receive 30 Daily Tasks:
   Day 1: Install Python & Hello World
   Day 2: Variables and data types
   ...
   Day 30: Final project presentation
   ↓
6. Daily Check-Ins:
   - Did you complete today's task?
   - What obstacles?
   - Confidence for tomorrow?
   - Get AI feedback
   ↓
7. Track Progress:
   Day 15/30 | 80% completion rate
   ↓
8. Celebrate Success! 🎉
```

## 📊 Technology Stack

- **Backend**: FastAPI + SQLAlchemy
- **AI**: LangGraph + LangChain + OpenAI
- **Database**: SQLite (dev) / PostgreSQL (prod)
- **Auth**: JWT + bcrypt
- **Frontend**: HTML/CSS/JS

## 🎯 Try It Now

### Example 1: Fitness Goal
```bash
curl -X POST http://localhost:8000/api/goalbot/goals/create \
  -H "Authorization: Bearer $TOKEN" \
  -d '{"goal": "Get in shape for summer"}'
```

### Example 2: Learning Goal
```bash
curl -X POST http://localhost:8000/api/goalbot/goals/create \
  -H "Authorization: Bearer $TOKEN" \
  -d '{"goal": "Learn to play guitar"}'
```

### Example 3: Career Goal
```bash
curl -X POST http://localhost:8000/api/goalbot/goals/create \
  -H "Authorization: Bearer $TOKEN" \
  -d '{"goal": "Build a portfolio website"}'
```

## 📚 Documentation

- **PRD**: `my_agent_prd.md` - Product requirements
- **README**: `GOALBOT_README.md` - Full documentation
- **Setup**: `GOALBOT_SETUP.md` - Detailed setup
- **Summary**: `IMPLEMENTATION_SUMMARY.md` - What was built

## 🚀 Next Steps

1. **Try it**: Create an account at http://localhost:8000/frontend/goalbot.html
2. **Set a goal**: Use the conversational interface
3. **Track progress**: Complete daily check-ins
4. **Explore**: Check API docs at http://localhost:8000/docs
5. **Customize**: Edit agent prompts in `backend/goalbot_agents.py`

## 🎉 Status

✅ **All features implemented**
✅ **All tests passing**
✅ **Zero linting errors**
✅ **Production-ready**

**Ready to help you achieve goals in 30 days!**

