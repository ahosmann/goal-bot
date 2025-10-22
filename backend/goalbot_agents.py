"""GoalBot AI agents for goal clarification, refinement, breakdown, and check-ins."""

from typing import Dict, Any, List, Optional, Annotated
from typing_extensions import TypedDict
import operator
import json

from langchain_core.messages import BaseMessage, HumanMessage, SystemMessage
from langchain_core.tools import tool
from langgraph.graph import StateGraph, END, START
from langgraph.prebuilt import ToolNode

# Import LLM from main
from main import llm

# Import tracing utilities for Arize AX observability
from arize_tracing import (
    is_tracing_enabled,
    using_prompt_template,
    using_attributes,
    get_current_span,
    set_span_attributes,
)

_TRACING = is_tracing_enabled()

# ============= Validation =============

def validate_goal_consistency(
    original_goal: str, 
    refined_goal: str, 
    daily_tasks: List[Dict[str, Any]], 
    milestones: Dict[str, str]
) -> Dict[str, Any]:
    """Validate that tasks and milestones match the actual goal.
    
    Catches issues like:
    - Walking goal suggesting strength training
    - Repetitive weekly milestones
    - Tasks that don't align with goal
    """
    warnings = []
    
    # Extract key terms from original goal
    original_lower = original_goal.lower()
    refined_lower = refined_goal.lower()
    
    # Check for mismatched activity types
    goal_keywords = {
        'walk': ['strength', 'weights', 'gym', 'lifting'],
        'run': ['swimming', 'cycling', 'weights'],
        'read': ['write', 'exercise', 'cook'],
        'meditate': ['exercise', 'workout', 'run'],
    }
    
    for goal_type, incompatible in goal_keywords.items():
        if goal_type in original_lower:
            # Check tasks for incompatible activities
            all_task_text = ' '.join([t.get('task', '').lower() for t in daily_tasks])
            for bad_word in incompatible:
                if bad_word in all_task_text:
                    warnings.append({
                        'type': 'activity_mismatch',
                        'message': f"Goal mentions '{goal_type}' but tasks include '{bad_word}'"
                    })
    
    # Check for repetitive milestones
    milestone_values = list(milestones.values())
    unique_starts = set()
    for m in milestone_values:
        # Extract first 30 chars to detect repetition
        start = m[:30].lower()
        if start in unique_starts:
            warnings.append({
                'type': 'repetitive_milestones',
                'message': 'Weekly milestones appear repetitive'
            })
            break
        unique_starts.add(start)
    
    return {
        'valid': len(warnings) == 0,
        'warnings': warnings
    }

# ============= State Management =============

class GoalState(TypedDict):
    """State for goal creation workflow."""
    messages: Annotated[List[BaseMessage], operator.add]
    
    # Input
    original_goal: str
    
    # Clarification phase
    clarification_questions: Optional[List[Dict[str, str]]]
    clarification_answers: Optional[Dict[str, str]]
    user_context: Optional[Dict[str, Any]]
    
    # Refinement phase
    refined_goal: Optional[str]
    goal_category: Optional[str]
    is_achievable: Optional[bool]
    refinement_reasoning: Optional[str]
    
    # Breakdown phase
    daily_tasks: Optional[List[Dict[str, Any]]]
    milestones: Optional[Dict[str, str]]
    
    # Tool tracking
    tool_calls: Annotated[List[Dict[str, Any]], operator.add]


# ============= Tools =============

@tool
def validate_goal_scope(goal: str, timeframe_days: int = 30) -> str:
    """Analyze if a goal is appropriately scoped for the given timeframe."""
    return f"Analyzing scope of '{goal}' for {timeframe_days} days..."


@tool
def suggest_goal_categories(goal: str) -> str:
    """Suggest relevant categories for a goal (fitness, learning, career, creativity, etc.)."""
    categories = ["fitness", "learning", "career", "creativity", "relationships", "wellness", "financial"]
    return f"Suggested categories: {', '.join(categories[:3])}"


@tool
def get_goal_templates(category: str) -> str:
    """Retrieve goal templates and best practices for a specific category."""
    templates = {
        "fitness": "SMART fitness goals include: specific metrics, progressive overload, recovery days",
        "learning": "Effective learning goals: daily practice, spaced repetition, practical projects",
        "career": "Career goals: skill building, networking milestones, tangible deliverables",
        "creativity": "Creative goals: daily creation habit, milestone projects, feedback loops"
    }
    return templates.get(category, "Focus on specific, measurable outcomes with daily actions")


# ============= Clarification Agent =============

def clarification_agent(state: GoalState) -> GoalState:
    """Agent that asks up to 3 clarifying questions about the user's goal."""
    original_goal = state["original_goal"]
    
    # Safety check for crisis language
    crisis_keywords = ['suicide', 'kill myself', 'want to die', 'end it all', 'self harm', 'hurt myself', 'no reason to live']
    if any(keyword in original_goal.lower() for keyword in crisis_keywords):
        return {
            "messages": [SystemMessage(content="Crisis intervention triggered")],
            "clarification_questions": [{
                "id": "crisis",
                "question": "I'm concerned about what you've shared. Please reach out to a trained crisis counselor who can provide immediate support. You can call or text 988 (available 24/7) or visit https://988lifeline.org/. Your safety is the priority.",
                "hint": ""
            }],
            "tool_calls": []
        }
    
    prompt = f"""You are a professional life coach mentor helping someone clarify their goal.

PERSONA: You are warm but professional, curious but focused. You act as a life coach who listens carefully to what the user said and probes deeper into their specific situation. You maintain a gender-neutral, judgment-free tone.

USER'S GOAL: "{original_goal}"

YOUR TASK: Generate EXACTLY 3 PERSONALIZED, CONTEXT-SPECIFIC clarifying questions based on what the user actually said in their goal.

CRITICAL: Analyze the user's specific goal and ask questions tailored to their situation. DO NOT use generic templates.

EXAMPLES OF CONTEXTUAL QUESTIONING:

If user says "I want to improve my relationships":
→ Ask: Which specific relationship do you want to focus on—family, friendships, or romantic?
→ Ask: What would "improved" look like to you?

If user says "I want to exercise more":
→ Ask: How active are you currently—mostly sedentary, or already doing some walking?
→ Ask: Would you prefer starting with something gentle like daily walks, or are you ready for more structured workouts?

If user says "I want to eat healthier":
→ Ask: What specific changes are you thinking about—eating more of certain foods (like vegetables) or cutting back on others (like fast food)?
→ Ask: Are there particular meals (breakfast, lunch, dinner) you want to focus on?

If user says "I want to be more productive":
→ Ask: What's getting in your way right now—procrastination, distractions, or feeling overwhelmed?
→ Ask: Which area of life needs this most—work, personal projects, or home?

YOUR QUESTIONS MUST:
- Be specific to what the user mentioned in their goal
- Probe deeper into their particular situation (not generic)
- Help understand their starting point, desired outcome, and constraints
- Feel like a life coach listening and digging deeper

TONE GUIDELINES:
- Be conversational but professional
- Use direct, clear language
- No exclamation points
- No emojis or slang
- Stay focused on the goal

Return questions as a JSON array:
[
  {{"id": "q1", "question": "Context-specific question based on their goal", "hint": "Brief hint"}},
  {{"id": "q2", "question": "Another personalized question", "hint": "Brief hint"}},
  {{"id": "q3", "question": "Third contextual question", "hint": "Brief hint"}}
]

Generate exactly 3 questions that are personalized to "{original_goal}" - NOT generic templates."""
    
    messages = [
        SystemMessage(content=prompt),
        HumanMessage(content=f"Goal: {original_goal}")
    ]
    
    # Instrument with Arize AX tracing
    with using_attributes(tags=["goalbot", "clarification"]):
        if _TRACING:
            current_span = get_current_span()
            if current_span:
                current_span.set_attribute("agent.type", "clarification")
                current_span.set_attribute("agent.goal", original_goal)
        
        with using_prompt_template(template=prompt, variables={"original_goal": original_goal}, version="v1"):
            response = llm.invoke(messages)
    
    # Parse questions from response
    try:
        # Try to extract JSON from response
        content = response.content
        if "```json" in content:
            content = content.split("```json")[1].split("```")[0]
        elif "```" in content:
            content = content.split("```")[1].split("```")[0]
        
        questions = json.loads(content.strip())
        
        if not isinstance(questions, list):
            questions = []
    except:
        # Fallback to open-ended questions
        questions = [
            {"id": "q1", "question": "Tell me more about your current situation with this goal. Where are you starting from?", "hint": "Be specific about where you are now"},
            {"id": "q2", "question": "What would success look like for you specifically in 30 days?", "hint": "Describe the concrete outcome you want"},
            {"id": "q3", "question": "What obstacles or constraints should we account for in your plan?", "hint": "Time, resources, current habits, etc."},
        ]
    
    return {
        "messages": [SystemMessage(content=response.content)],
        "clarification_questions": questions,
        "tool_calls": []
    }


# ============= Refinement Agent =============

def refinement_agent(state: GoalState) -> GoalState:
    """Agent that refines the goal into a SMART 30-day version with safety validation."""
    original_goal = state["original_goal"]
    clarification_answers = state.get("clarification_answers", {})
    
    # Safety check for unhealthy/dangerous goals
    unsafe_patterns = [
        ('lose.*\d{2,}.*pounds?', 'Rapid weight loss can be harmful. Would you be open to a goal of developing sustainable healthy habits?'),
        ('stop.*sleep|no.*sleep|sleep.*\d hour', 'Sleep is essential for health. What if we focused on optimizing your waking hours instead?'),
        ('extreme|dangerous|risky', 'This goal may pose health risks. Let me suggest a safer alternative.'),
    ]
    
    import re
    for pattern, suggestion in unsafe_patterns:
        if re.search(pattern, original_goal.lower()):
            return {
                "messages": [SystemMessage(content=f"Safety concern detected: {suggestion}")],
                "refined_goal": None,
                "goal_category": "unsafe",
                "is_achievable": False,
                "refinement_reasoning": "Goal requires modification for safety",
                "tool_calls": []
            }
    
    # Build context from clarification
    context = "\n".join([f"Q: {q}\nA: {a}" for q, a in clarification_answers.items()])
    
    prompt = f"""You are a professional business mentor helping someone refine their goal into an achievable 30-day plan.

PERSONA: You are advisory, practical, and direct. You balance realism with encouragement. You communicate clearly without jargon or clichés.

ORIGINAL GOAL: "{original_goal}"

CLARIFICATION CONTEXT:
{context}

YOUR TASK: Refine this into a SMART goal achievable in 30 days:
- Specific: Clear, concrete outcome
- Measurable: Quantifiable success criteria  
- Achievable: Realistic for average USA adult with typical constraints (work, family, 30-60 min/day)
- Relevant: Aligned with their motivation
- Time-bound: 30-day timeframe

SAFETY: If goal involves health, fitness, diet, or mental health, suggest consulting appropriate professionals. Never provide medical advice.

CRITICAL - MAINTAIN GOAL SPECIFICITY:
- If user mentions "walking", refined goal should focus on WALKING specifically
- If user mentions "running", refined goal should focus on RUNNING specifically  
- If user mentions "reading", refined goal should focus on READING specifically
- Do NOT generalize "walking" to "exercise" or "cardio and strength"
- Do NOT generalize "reading" to "learning"
- Keep the specific activity the user mentioned in their goal

TONE GUIDELINES:
- Be clear and direct about what's realistic
- If the goal is too ambitious, scope it down professionally
- Use "you" not "we" or "let's"
- No motivational clichés or sports metaphors
- No exclamation points

Respond in JSON format:
{{
  "refined_goal": "The SMART 30-day goal",
  "category": "fitness/learning/career/creativity/wellness/financial/relationships",
  "is_achievable": true/false,
  "reasoning": "Brief, professional explanation of why you refined it this way"
}}"""
    
    messages = [
        SystemMessage(content=prompt),
        HumanMessage(content=f"Refine this goal for a 30-day sprint")
    ]
    
    # Instrument with Arize AX tracing
    with using_attributes(tags=["goalbot", "refinement"]):
        if _TRACING:
            current_span = get_current_span()
            if current_span:
                current_span.set_attribute("agent.type", "refinement")
                current_span.set_attribute("agent.goal", original_goal)
        
        with using_prompt_template(template=prompt, variables={"original_goal": original_goal, "context": context}, version="v1"):
            response = llm.invoke(messages)
    
    # Parse refinement from response
    try:
        content = response.content
        if "```json" in content:
            content = content.split("```json")[1].split("```")[0]
        elif "```" in content:
            content = content.split("```")[1].split("```")[0]
        
        refinement = json.loads(content.strip())
    except:
        # Fallback refinement
        refinement = {
            "refined_goal": original_goal,
            "category": "general",
            "is_achievable": True,
            "reasoning": "Goal accepted as stated"
        }
    
    return {
        "messages": [SystemMessage(content=response.content)],
        "refined_goal": refinement.get("refined_goal", original_goal),
        "goal_category": refinement.get("category", "general"),
        "is_achievable": refinement.get("is_achievable", True),
        "refinement_reasoning": refinement.get("reasoning", ""),
        "tool_calls": []
    }


# ============= Breakdown Agent =============

def breakdown_agent(state: GoalState) -> GoalState:
    """Agent that creates 4 weekly mini-goals and detailed daily tasks for Week 1."""
    refined_goal = state.get("refined_goal", state["original_goal"])
    category = state.get("goal_category", "general")
    context = state.get("user_context", {})
    
    prompt = f"""You are a professional business mentor with project management expertise creating a structured 30-day action plan.

PERSONA: You are systematic, clear, and practical. You excel at breaking down large goals into progressive milestones that build upon each other.

REFINED GOAL: "{refined_goal}"
CATEGORY: {category}

YOUR TASK: Create a weekly progression plan with:
1. Four weekly mini-goals that BUILD PROGRESSIVELY (Weeks 1-4)
2. Detailed daily tasks for ALL 30 days with clear success criteria
3. Time estimates for each task (30-60 min is typical)

PROJECT MANAGEMENT METHODOLOGY - PROGRESSIVE MILESTONE DESIGN:

Each weekly milestone MUST build upon the previous week following this pattern:
- Week 1: FOUNDATION - Establish baseline, learn fundamentals, create initial habit
- Week 2: DEVELOPMENT - Build consistency, increase capacity, strengthen routine
- Week 3: ADVANCEMENT - Push beyond comfort zone, add complexity, deepen practice
- Week 4: ACHIEVEMENT - Reach stretch goal, demonstrate mastery, accomplish final objective

CRITICAL - ANTI-PATTERN (DO NOT DO THIS):
❌ Week 1: Exercise 3 times
❌ Week 2: Exercise 3 times [WRONG - This is repetition]
❌ Week 3: Exercise 3 times [WRONG - This is repetition]
❌ Week 4: Exercise 3 times [WRONG - This is repetition]

CORRECT PATTERN - PROGRESSIVE MILESTONES:
✓ Week 1: Foundation - Establish habit (3 x 20-min walks)
✓ Week 2: Development - Build endurance (3 x 30-min walks at faster pace)
✓ Week 3: Advancement - Add variety (2 walks + 1 beginner strength session)
✓ Week 4: Achievement - Reach goal (4 x 30-min mixed cardio/strength workouts)

MILESTONE REQUIREMENTS:
- Each milestone is a meaningful checkpoint toward the end goal
- Clear differentiation between weeks (NOT just repetition)
- Builds skills/capacity needed for subsequent milestones
- Weekly goals form a logical progression story
- Label each week with its phase (Foundation/Development/Advancement/Achievement)

TONE GUIDELINES:
- Write tasks in simple, direct language
- Use action verbs (complete, practice, build, review)
- No motivational language or cheerleading
- Keep task descriptions concise (one sentence each)
- Success criteria should be measurable

Respond in JSON format:
{{
  "daily_tasks": [
    {{"day": 1, "task": "Clear, specific task for day 1", "success_criteria": "Measurable outcome", "estimated_time": "30 min"}},
    {{"day": 2, "task": "...", "success_criteria": "...", "estimated_time": "30 min"}},
    ... (all 30 days)
  ],
  "milestones": {{
    "day_7": "Week 1 (Foundation): [Specific foundation milestone with clear baseline]",
    "day_14": "Week 2 (Development): [Specific development milestone showing growth]",
    "day_21": "Week 3 (Advancement): [Specific advancement milestone with increased challenge]",
    "day_30": "Week 4 (Achievement): {refined_goal}"
  }}
}}

REMEMBER: Each week must show clear progression and be distinctly different from the previous week. User will see Weeks 1-4 summary + Days 1-7 details upfront."""
    
    messages = [
        SystemMessage(content=prompt),
        HumanMessage(content="Create the 30-day breakdown")
    ]
    
    # Instrument with Arize AX tracing
    with using_attributes(tags=["goalbot", "breakdown"]):
        if _TRACING:
            current_span = get_current_span()
            if current_span:
                current_span.set_attribute("agent.type", "breakdown")
                current_span.set_attribute("agent.goal", refined_goal)
                current_span.set_attribute("agent.category", category)
        
        with using_prompt_template(template=prompt, variables={"refined_goal": refined_goal, "category": category}, version="v1"):
            response = llm.invoke(messages)
    
    # Parse breakdown from response
    try:
        content = response.content
        if "```json" in content:
            content = content.split("```json")[1].split("```")[0]
        elif "```" in content:
            content = content.split("```")[1].split("```")[0]
        
        breakdown = json.loads(content.strip())
        daily_tasks = breakdown.get("daily_tasks", [])
        milestones = breakdown.get("milestones", {})
    except:
        # Fallback: create simple 30-day tasks
        daily_tasks = [
            {
                "day": i,
                "task": f"Day {i}: Work toward {refined_goal}",
                "success_criteria": "Complete today's focused work",
                "estimated_time": "30-60 min"
            }
            for i in range(1, 31)
        ]
        milestones = {
            "day_7": f"Week 1 (Foundation): Establish baseline for {refined_goal}",
            "day_14": f"Week 2 (Development): Build consistency and momentum",
            "day_21": f"Week 3 (Advancement): Push beyond initial level",
            "day_30": f"Week 4 (Achievement): {refined_goal}"
        }
    
    # Validate consistency
    validation = validate_goal_consistency(
        original_goal=state.get("original_goal", ""),
        refined_goal=refined_goal,
        daily_tasks=daily_tasks,
        milestones=milestones
    )
    
    # If validation fails, retry with stronger prompt
    if not validation['valid']:
        warnings_text = '\n'.join([w['message'] for w in validation['warnings']])
        
        retry_prompt = f"""CRITICAL VALIDATION FAILED:
{warnings_text}

The breakdown you created does NOT match the user's goal. 

ORIGINAL GOAL: "{state.get('original_goal', '')}"
REFINED GOAL: "{refined_goal}"

You MUST:
1. Create tasks that DIRECTLY relate to the stated goal
2. If goal is about WALKING, do NOT include strength training, gym, or weights
3. If goal is about READING, do NOT include exercise or cooking
4. Make each week DISTINCTLY DIFFERENT (not repetitive)

Generate a corrected breakdown now."""

        retry_messages = [
            SystemMessage(content=prompt),
            HumanMessage(content=retry_prompt)
        ]
        
        # Instrument retry with tracing
        with using_attributes(tags=["goalbot", "breakdown_retry"]):
            if _TRACING:
                current_span = get_current_span()
                if current_span:
                    current_span.set_attribute("agent.retry", True)
                    current_span.set_attribute("agent.validation_failed", True)
            
            retry_response = llm.invoke(retry_messages)
        
        # Re-parse
        try:
            content = retry_response.content
            if "```json" in content:
                content = content.split("```json")[1].split("```")[0]
            elif "```" in content:
                content = content.split("```")[1].split("```")[0]
            
            breakdown = json.loads(content.strip())
            daily_tasks = breakdown.get("daily_tasks", daily_tasks)
            milestones = breakdown.get("milestones", milestones)
        except:
            pass  # Keep original if retry fails
    
    return {
        "messages": [SystemMessage(content=response.content)],
        "daily_tasks": daily_tasks,
        "milestones": milestones,
        "tool_calls": []
    }


# ============= Check-In Agent =============

def checkin_agent(
    goal: str,
    day_number: int,
    today_task: Dict[str, Any],
    task_completed: bool,
    user_response: str,
    obstacles: Optional[str],
    confidence_level: int,
    recent_check_ins: List[Dict[str, Any]]
) -> Dict[str, Any]:
    """Agent for daily check-ins with accountability and safety monitoring."""
    
    # Crisis detection in user responses
    crisis_keywords = ['suicide', 'kill myself', 'want to die', 'end it all', 'self harm', 'hurt myself', 'no reason to live', 'no point']
    combined_text = f"{user_response} {obstacles or ''}".lower()
    
    if any(keyword in combined_text for keyword in crisis_keywords):
        return {
            "feedback": "I'm concerned about what you've shared. Please reach out to a trained crisis counselor who can provide immediate support. You can call or text 988 (available 24/7) or visit https://988lifeline.org/. Your safety is the priority.",
            "crisis_detected": True,
            "adjusted_plan": None,
            "agent_assessment": {
                "momentum": "crisis_intervention_needed",
                "intervention_needed": True
            }
        }
    
    # Build context from recent check-ins
    history_context = ""
    if recent_check_ins:
        history_context = "Recent progress:\n"
        for ci in recent_check_ins[-5:]:  # Last 5 check-ins
            status = "Completed" if ci.get("task_completed") else "Missed"
            history_context += f"Day {ci['day_number']}: {status} (confidence: {ci['confidence_level']}/5)\n"
    
    prompt = f"""You are a professional business mentor conducting a daily check-in on a 30-day goal.

PERSONA: You are consistent, constructive, and focused on accountability. You acknowledge both progress and setbacks professionally. You stay positive without toxic positivity.

GOAL: {goal}
DAY: {day_number}/30
TODAY'S TASK: {today_task.get('task', 'N/A')}

CHECK-IN DATA:
- Task completed: {"Yes" if task_completed else "No"}
- User's response: {user_response}
- Obstacles faced: {obstacles or "None mentioned"}
- Confidence for tomorrow: {confidence_level}/5

{history_context}

YOUR RESPONSE SHOULD INCLUDE:
1. ACKNOWLEDGMENT - Brief recognition of today's result (1 sentence)
2. CONTEXT - Where they are in the 30-day plan (1 sentence)
3. GUIDANCE - Specific next step or adjustment if needed (1-2 sentences)

TONE GUIDELINES:
- Be direct and clear
- Use "You completed/missed" not "Great job!" or "That's disappointing!"
- No exclamation points (use period: "That's progress.")
- If they're struggling, ask what needs to change
- Keep it under 150 words
- No emojis, no slang, no clichés

Provide professional, constructive feedback that keeps them accountable."""
    
    messages = [
        SystemMessage(content=prompt),
        HumanMessage(content="Provide check-in feedback")
    ]
    
    # Instrument with Arize AX tracing
    with using_attributes(tags=["goalbot", "checkin"]):
        if _TRACING:
            current_span = get_current_span()
            if current_span:
                current_span.set_attribute("agent.type", "checkin")
                current_span.set_attribute("agent.goal", goal)
                current_span.set_attribute("agent.day", day_number)
                current_span.set_attribute("agent.task_completed", task_completed)
                current_span.set_attribute("agent.confidence", confidence_level)
        
        with using_prompt_template(template=prompt, variables={"goal": goal, "day_number": day_number}, version="v1"):
            response = llm.invoke(messages)
    
    feedback = response.content
    
    # Determine if plan adjustment needed
    adjusted_plan = None
    if not task_completed or confidence_level <= 2:
        adjusted_plan = {
            "suggestion": "Consider breaking tomorrow's task into smaller steps",
            "recommended_action": "Reduce scope or add more support"
        }
    
    return {
        "feedback": feedback,
        "adjusted_plan": adjusted_plan,
        "agent_assessment": {
            "momentum": "strong" if task_completed and confidence_level >= 4 else "needs_support",
            "intervention_needed": confidence_level <= 2
        }
    }


# ============= LangGraph Workflow =============

def build_goal_creation_graph():
    """Build the LangGraph workflow for goal creation (Clarification → Refinement → Breakdown)."""
    graph = StateGraph(GoalState)
    
    # Add agent nodes
    graph.add_node("clarification", clarification_agent)
    graph.add_node("refinement", refinement_agent)
    graph.add_node("breakdown", breakdown_agent)
    
    # Sequential flow
    graph.add_edge(START, "clarification")
    graph.add_edge("clarification", "refinement")
    graph.add_edge("refinement", "breakdown")
    graph.add_edge("breakdown", END)
    
    return graph.compile()

