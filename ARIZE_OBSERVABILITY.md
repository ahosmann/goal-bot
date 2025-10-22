# Arize AX Observability Setup

This document explains how to set up **Arize AX** (not Phoenix) observability for the GoalBot & AI Trip Planner application to visualize and monitor your AI agents.

## 🎯 What You'll Get

With Arize AX tracing enabled, you'll be able to:

- **Visualize agent workflows** - See how your LangGraph agents (research, budget, local, itinerary, GoalBot clarification, etc.) execute in real-time
- **Monitor LLM calls** - Track all OpenAI/LLM API calls with prompts, responses, and latencies
- **Debug tool executions** - Inspect tool calls (search, budget analysis, local guides retrieval) with inputs and outputs
- **Track sessions** - Group related traces by session_id and user_id
- **Analyze prompt templates** - See which prompts are being used and their performance
- **Monitor RAG pipelines** - Track vector search queries and retrieved documents

## 📋 Prerequisites

1. **Arize Account** - Sign up at [https://app.arize.com/](https://app.arize.com/)
2. **Python 3.10+** - The application requires Python 3.10 or higher
3. **OpenAI API Key** - Required for the LLM (or OpenRouter as alternative)

## 🚀 Quick Start

### Step 1: Get Your Arize Credentials

1. Log in to [Arize](https://app.arize.com/)
2. Navigate to **Space Settings** > **API Keys**
3. Copy your:
   - **Space ID** (also called Space Key)
   - **API Key**

### Step 2: Set Environment Variables

Add the following to your `backend/.env` file:

```bash
# Arize AX Observability
ARIZE_SPACE_ID=your_space_id_here
ARIZE_API_KEY=your_api_key_here
ARIZE_PROJECT_NAME=goalbot-ai-trip-planner

# Your OpenAI API Key (required for LLM)
OPENAI_API_KEY=your_openai_api_key_here
```

### Step 3: Install Dependencies

```bash
cd backend
pip install -r requirements.txt
```

**Note for macOS users:** If you get `pip: command not found`, use `pip3` instead:
```bash
pip3 install -r requirements.txt
# or
python3 -m pip install -r requirements.txt
```

This will install:
- `arize-otel>=0.8.1` - Arize OpenTelemetry integration
- `openinference-instrumentation-langchain>=0.1.19` - LangChain/LangGraph auto-instrumentation
- `openinference-instrumentation-openai>=0.1.0` - OpenAI auto-instrumentation
- `opentelemetry-sdk>=1.21.0` - OpenTelemetry core

### Step 4: Start the Application

```bash
cd backend
python main.py
```

Or with uvicorn:

```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

**Note for macOS users:** Use `python3` if `python` is not found:
```bash
python3 main.py
# or
python3 -m uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

You should see in the startup logs:

```
✓ LangChain/LangGraph instrumented
✓ OpenAI instrumented
✓ LiteLLM instrumented
🎉 Arize AX tracing initialized successfully!
   Project: goalbot-ai-trip-planner
   Space ID: abc12345...
   View traces at: https://app.arize.com/organizations/abc12345/spaces
```

### Step 5: Verify Tracing

1. Make a request to the API (e.g., create a trip plan or goal)
2. Go to [https://app.arize.com/](https://app.arize.com/)
3. Navigate to your **Space** > **Traces**
4. You should see traces appearing in real-time!

## 📊 What Gets Traced

### Trip Planner Agents

1. **Research Agent** (`research_agent`)
   - Tools: `essential_info`, `weather_brief`, `visa_brief`
   - Tags: `research`, `info_gathering`
   - Metadata: `agent_type`, `agent_node`

2. **Budget Agent** (`budget_agent`)
   - Tools: `budget_basics`, `attraction_prices`
   - Tags: `budget`, `cost_analysis`
   - Metadata: `agent_type`, `agent_node`

3. **Local Agent** (`local_agent`)
   - Tools: `local_flavor`, `local_customs`, `hidden_gems`
   - RAG: Vector search for curated local guides (when `ENABLE_RAG=1`)
   - Tags: `local`, `local_experiences`
   - Metadata: `agent_type`, `agent_node`, `rag_enabled`

4. **Itinerary Agent** (`itinerary_agent`)
   - Synthesizes all agent outputs into final itinerary
   - Tags: `itinerary`, `final_agent`
   - Metadata: `agent_type`, `agent_node`, `user_input`

### GoalBot Agents

1. **Clarification Agent** (`clarification_agent`)
   - Generates personalized clarifying questions
   - Tags: `goalbot`, `clarification`
   - Metadata: `agent.type`, `agent.goal`

2. **Refinement Agent** (`refinement_agent`)
   - Refines user goal into SMART 30-day goal
   - Tags: `goalbot`, `refinement`
   - Metadata: `agent.type`, `agent.goal`

3. **Breakdown Agent** (`breakdown_agent`)
   - Creates 30-day task breakdown with milestones
   - Tags: `goalbot`, `breakdown`
   - Metadata: `agent.type`, `agent.goal`, `agent.category`

4. **Check-in Agent** (`checkin_agent`)
   - Daily check-ins and feedback
   - Tags: `goalbot`, `checkin`
   - Metadata: `agent.type`, `agent.day`, `agent.task_completed`, `agent.confidence`

### LLM Calls

All LLM calls are automatically instrumented with:
- **Model name** (e.g., `gpt-4o`)
- **Prompt** (input messages)
- **Response** (generated text)
- **Token counts** (input/output tokens)
- **Latency** (response time)
- **Prompt template metadata** (template, variables, version)

### Tool Calls

All LangChain tools are automatically traced:
- Tool name
- Input arguments
- Output/results
- Execution time
- Success/error status

## 🔧 Advanced Configuration

### Custom Project Name

Change the project name in Arize:

```bash
ARIZE_PROJECT_NAME=my-custom-project-name
```

### Session and User Tracking

The trip planner already supports session and user tracking. Pass these in your requests:

```python
import requests

response = requests.post("http://localhost:8000/plan-trip", json={
    "destination": "Paris",
    "duration": "7 days",
    "session_id": "session-123",  # Groups related requests
    "user_id": "user-456",        # Tracks individual users
    "turn_index": 1                # Conversation turn number
})
```

These will automatically appear in Arize as span attributes:
- `session_id`
- `user_id`
- `turn_index`

### RAG Tracing

Enable RAG for local guides retrieval:

```bash
ENABLE_RAG=1
```

This will trace:
- Vector embeddings generation
- Similarity search queries
- Retrieved documents
- Context injection into prompts

### Disable Tracing

To disable tracing even when credentials are set:

```bash
ENABLE_TRACING=0
```

Or simply remove/comment out `ARIZE_SPACE_ID` and `ARIZE_API_KEY`.

## 📈 Viewing Traces in Arize

### Trace View

In Arize, you'll see traces organized as:

```
plan_trip (root span)
├── research_agent
│   ├── essential_info (tool)
│   ├── weather_brief (tool)
│   └── visa_brief (tool)
├── budget_agent
│   ├── budget_basics (tool)
│   └── attraction_prices (tool)
├── local_agent
│   ├── vector_search (RAG - if enabled)
│   ├── local_flavor (tool)
│   └── hidden_gems (tool)
└── itinerary_agent
    └── llm_synthesis
```

### Key Metrics to Monitor

1. **Latency** - How long each agent takes
2. **Token Usage** - Cost tracking per LLM call
3. **Error Rates** - Failed tool calls or LLM errors
4. **Tool Success Rates** - Which tools work best
5. **Session Flow** - Multi-turn conversation patterns

### Filtering and Search

Use Arize's search to filter traces by:
- `tags` - e.g., `tags:research` or `tags:goalbot`
- `metadata.agent_type` - e.g., `metadata.agent_type:budget`
- `session_id` - e.g., `session_id:session-123`
- `user_id` - e.g., `user_id:user-456`

## 🐛 Debugging with Arize

### Common Issues

**1. "pip: command not found" (macOS)**
- Use `pip3` instead: `pip3 install -r requirements.txt`
- Or use Python module syntax: `python3 -m pip install -r requirements.txt`
- If still not found, install pip: `curl https://bootstrap.pypa.io/get-pip.py -o get-pip.py && python3 get-pip.py`

**2. No traces appearing**
- Check that `ARIZE_SPACE_ID` and `ARIZE_API_KEY` are set correctly
- Verify you see the "🎉 Arize AX tracing initialized" message on startup
- Check your Arize Space ID matches the one in your .env
- Ensure your API key has write permissions

**3. Incomplete traces**
- Check for errors in application logs
- Verify all dependencies are installed: `pip3 install -r requirements.txt`
- Make sure you're using the correct OpenTelemetry versions

**4. Slow performance**
- Tracing adds minimal overhead (~5-10ms per request)
- If experiencing issues, temporarily disable with `ENABLE_TRACING=0`

### Viewing Prompt Templates

Arize's **Playground** feature allows you to:
- View the exact prompts used by each agent
- See template variables (destination, duration, budget, etc.)
- Experiment with prompt modifications
- Compare prompt versions

Look for spans with `openinference.prompt_template` attributes.

## 📚 Additional Resources

- **Arize Documentation**: [https://docs.arize.com/](https://docs.arize.com/)
- **OpenInference Spec**: [https://github.com/Arize-ai/openinference](https://github.com/Arize-ai/openinference)
- **LangChain Integration**: [https://docs.arize.com/arize/llm-large-language-models/llm-traces/langchain](https://docs.arize.com/arize/llm-large-language-models/llm-traces/langchain)

## 🔐 Security Best Practices

1. **Never commit `.env` files** - They're in `.gitignore` by default
2. **Rotate API keys** - Regularly rotate your Arize and OpenAI keys
3. **Use environment-specific keys** - Different keys for dev/staging/prod
4. **Limit key permissions** - Use read-only keys where possible

## 🤝 Support

If you encounter issues:

1. Check application logs for tracing initialization messages
2. Verify your Arize credentials at [https://app.arize.com/](https://app.arize.com/)
3. Review the [Arize documentation](https://docs.arize.com/)
4. Check the `arize_tracing.py` module for detailed logging

## 📝 Architecture Overview

The observability implementation consists of:

1. **`arize_tracing.py`** - Centralized tracing configuration module
   - Initializes Arize tracer provider
   - Instruments LangChain, OpenAI, and LiteLLM
   - Provides helper functions for manual instrumentation

2. **`main.py`** - Trip planner with instrumented agents
   - Research, Budget, Local, and Itinerary agents
   - Session/user tracking
   - Prompt template tracking

3. **`goalbot_agents.py`** - GoalBot with instrumented agents
   - Clarification, Refinement, Breakdown, Check-in agents
   - Goal tracking and validation

All instrumentation uses:
- **OpenTelemetry** - Industry-standard tracing framework
- **OpenInference** - LLM-specific semantic conventions
- **Arize OTEL** - Seamless integration with Arize platform

---

**Happy Tracing! 🎉**

Your AI agents are now fully observable in Arize AX. Monitor, debug, and optimize your application with confidence.

