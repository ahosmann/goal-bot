# Arize AX Quick Reference

## 🚀 Quick Start (30 seconds)

```bash
# 1. Add to backend/.env
ARIZE_SPACE_ID=your_space_id_here
ARIZE_API_KEY=your_api_key_here

# 2. Install dependencies (use pip3 on macOS)
pip3 install -r requirements.txt

# 3. Start the app (use python3 on macOS)
python3 main.py
```

## 📍 Where to Get Credentials

1. Go to [https://app.arize.com/](https://app.arize.com/)
2. **Space Settings** → **API Keys**
3. Copy **Space ID** and **API Key**

## 🔍 View Traces

[https://app.arize.com/](https://app.arize.com/) → Your Space → **Traces**

## 📊 What's Traced

### Trip Planner
- ✅ Research Agent (weather, visa, essentials)
- ✅ Budget Agent (costs, pricing)
- ✅ Local Agent (experiences, RAG retrieval)
- ✅ Itinerary Agent (final synthesis)

### GoalBot
- ✅ Clarification Agent (questions)
- ✅ Refinement Agent (SMART goals)
- ✅ Breakdown Agent (30-day tasks)
- ✅ Check-in Agent (daily feedback)

### Automatic
- ✅ All LLM calls (prompts, responses, tokens)
- ✅ All tool executions
- ✅ RAG vector searches (when enabled)
- ✅ Session/user tracking

## 🎛️ Configuration

```bash
# Optional: Custom project name
ARIZE_PROJECT_NAME=my-project

# Optional: Enable RAG tracing
ENABLE_RAG=1

# Optional: Disable tracing
ENABLE_TRACING=0
```

## 🔗 Session Tracking

Pass in API requests:

```python
{
  "destination": "Paris",
  "duration": "7 days",
  "session_id": "session-123",  # Groups requests
  "user_id": "user-456",        # Tracks users
  "turn_index": 1                # Conversation turn
}
```

## 📁 Key Files

- `backend/arize_tracing.py` - Tracing configuration
- `backend/main.py` - Trip planner with tracing
- `backend/goalbot_agents.py` - GoalBot with tracing
- `ARIZE_OBSERVABILITY.md` - Full documentation

## 🆘 Troubleshooting

**"pip: command not found" (macOS)?**
- Use `pip3 install -r requirements.txt`
- Or use `python3 -m pip install -r requirements.txt`

**No traces?**
- Check credentials in `.env`
- Look for "🎉 Arize AX tracing initialized" in logs
- Verify Space ID matches Arize dashboard

**Need help?**
- See `ARIZE_OBSERVABILITY.md` for full guide
- Check logs in `arize_tracing.py`
- Visit [docs.arize.com](https://docs.arize.com/)

---

**That's it! Your agents are now fully observable in Arize AX** 🎉

