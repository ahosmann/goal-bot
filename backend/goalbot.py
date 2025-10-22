"""GoalBot API routes for goal management and check-ins."""

from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session
from datetime import datetime
from typing import List

from database import get_db, init_db
from models import User, Goal, DailyCheckIn
from schemas import (
    UserSignup, UserLogin, Token, UserResponse,
    GoalCreate, ClarificationResponse, GoalResponse, GoalDetail,
    CheckInCreate, CheckInResponse, ProgressSummary,
    ClarificationSession, RefinedGoalResult, GoalBreakdown
)
from auth import (
    get_password_hash, verify_password, create_access_token,
    get_current_user_id, get_current_user
)
from goalbot_agents import build_goal_creation_graph, checkin_agent

# Create router
router = APIRouter()


# ============= Session Management (MVP Privacy) =============

def get_session_id(request: Request) -> str:
    """Extract session ID from request headers for MVP privacy."""
    session_id = request.headers.get('X-Session-ID', 'default-session')
    return session_id


# ============= Authentication Routes =============

@router.post("/signup", response_model=Token, status_code=status.HTTP_201_CREATED)
def signup(user_data: UserSignup, db: Session = Depends(get_db)):
    """Create a new user account."""
    # Check if email exists
    if db.query(User).filter(User.email == user_data.email).first():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # Check if username exists
    if db.query(User).filter(User.username == user_data.username).first():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already taken"
        )
    
    # Create user
    hashed_password = get_password_hash(user_data.password)
    new_user = User(
        email=user_data.email,
        username=user_data.username,
        hashed_password=hashed_password
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
    # Create access token
    access_token = create_access_token(data={"sub": str(new_user.id)})
    
    return Token(access_token=access_token)


@router.post("/login", response_model=Token)
def login(login_data: UserLogin, db: Session = Depends(get_db)):
    """Login and get access token."""
    # Find user
    user = db.query(User).filter(User.email == login_data.email).first()
    if not user or not verify_password(login_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password"
        )
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Account is inactive"
        )
    
    # Create access token
    access_token = create_access_token(data={"sub": str(user.id)})
    
    return Token(access_token=access_token)


@router.get("/me", response_model=UserResponse)
def get_current_user_info(user_id: int = Depends(get_current_user_id), db: Session = Depends(get_db)):
    """Get current user information."""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


# ============= Goal Creation Routes =============

@router.post("/goals/create", response_model=ClarificationSession, status_code=status.HTTP_201_CREATED)
def create_goal(
    goal_data: GoalCreate,
    request: Request,
    db: Session = Depends(get_db)
):
    """Step 1: Create a goal and get clarification questions."""
    # Get session ID for MVP privacy
    session_id = get_session_id(request)
    
    # For MVP: Use anonymous user (user_id = 1)
    # Create default user if not exists
    default_user = db.query(User).filter(User.id == 1).first()
    if not default_user:
        default_user = User(
            id=1,
            email="anonymous@goalbot.local",
            username="anonymous",
            hashed_password="not_used_in_mvp"
        )
        db.add(default_user)
        db.commit()
    
    # Create goal record in database with session_id
    new_goal = Goal(
        user_id=1,  # Anonymous user for MVP
        session_id=session_id,  # Device-specific session for privacy
        original_goal=goal_data.goal,
        status="clarifying"
    )
    db.add(new_goal)
    db.commit()
    db.refresh(new_goal)
    
    # Run clarification agent
    graph = build_goal_creation_graph()
    state = {
        "original_goal": goal_data.goal,
        "messages": [],
        "tool_calls": []
    }
    
    # Invoke just the clarification step
    result = graph.invoke(state, {"recursion_limit": 10})
    
    questions = result.get("clarification_questions", [])
    
    # Store questions in goal record
    new_goal.clarification_qa = {"questions": questions, "answers": {}}
    db.commit()
    
    return ClarificationSession(
        goal_id=new_goal.id,
        questions=[
            {"question_id": q["id"], "question": q["question"], "hint": q.get("hint")}
            for q in questions
        ]
    )


@router.post("/goals/{goal_id}/clarify", response_model=RefinedGoalResult)
def submit_clarification(
    goal_id: int,
    responses: ClarificationResponse,
    request: Request,
    db: Session = Depends(get_db)
):
    """Step 2: Submit clarification answers and get refined goal."""
    # Get goal - verify session for privacy
    session_id = get_session_id(request)
    goal = db.query(Goal).filter(Goal.id == goal_id, Goal.session_id == session_id).first()
    if not goal:
        raise HTTPException(status_code=404, detail="Goal not found")
    
    if goal.status != "clarifying":
        raise HTTPException(status_code=400, detail="Goal is not in clarification phase")
    
    # Update clarification answers
    qa_data = goal.clarification_qa or {}
    qa_data["answers"] = responses.answers
    goal.clarification_qa = qa_data
    
    # Run refinement agent
    graph = build_goal_creation_graph()
    state = {
        "original_goal": goal.original_goal,
        "clarification_answers": responses.answers,
        "messages": [],
        "tool_calls": []
    }
    
    result = graph.invoke(state)
    
    # Update goal with refined version
    goal.refined_goal = result.get("refined_goal", goal.original_goal)
    goal.goal_category = result.get("goal_category", "general")
    goal.user_context = {
        "is_achievable": result.get("is_achievable", True),
        "reasoning": result.get("refinement_reasoning", "")
    }
    goal.status = "refining"
    db.commit()
    
    return RefinedGoalResult(
        goal_id=goal.id,
        original_goal=goal.original_goal,
        refined_goal=goal.refined_goal,
        goal_category=goal.goal_category,
        reasoning=result.get("refinement_reasoning", ""),
        is_achievable_in_30_days=result.get("is_achievable", True)
    )


@router.post("/goals/{goal_id}/breakdown", response_model=GoalBreakdown)
def create_breakdown(
    goal_id: int,
    request: Request,
    db: Session = Depends(get_db)
):
    """Step 3: Generate 30-day breakdown and activate goal."""
    # Get goal - verify session for privacy
    session_id = get_session_id(request)
    goal = db.query(Goal).filter(Goal.id == goal_id, Goal.session_id == session_id).first()
    if not goal:
        raise HTTPException(status_code=404, detail="Goal not found")
    
    if goal.status not in ["clarifying", "refining"]:
        raise HTTPException(status_code=400, detail="Goal already has a breakdown")
    
    # Run breakdown agent
    graph = build_goal_creation_graph()
    state = {
        "original_goal": goal.original_goal,
        "refined_goal": goal.refined_goal or goal.original_goal,
        "goal_category": goal.goal_category or "general",
        "messages": [],
        "tool_calls": []
    }
    
    result = graph.invoke(state)
    
    # Update goal with breakdown
    goal.daily_tasks = result.get("daily_tasks", [])
    goal.milestones = result.get("milestones", {})
    goal.status = "active"
    goal.started_at = datetime.utcnow()
    goal.current_day = 0
    db.commit()
    
    return GoalBreakdown(
        goal_id=goal.id,
        daily_tasks=goal.daily_tasks,
        milestones=goal.milestones
    )


# ============= Goal Management Routes =============

@router.get("/goals", response_model=List[GoalResponse])
def list_goals(
    request: Request,
    db: Session = Depends(get_db)
):
    """List all goals for current session (device-specific for MVP privacy)."""
    session_id = get_session_id(request)
    goals = db.query(Goal).filter(Goal.session_id == session_id).order_by(Goal.created_at.desc()).all()
    return goals


@router.get("/goals/{goal_id}", response_model=GoalDetail)
def get_goal(
    goal_id: int,
    request: Request,
    db: Session = Depends(get_db)
):
    """Get detailed information about a specific goal."""
    session_id = get_session_id(request)
    goal = db.query(Goal).filter(Goal.id == goal_id, Goal.session_id == session_id).first()
    if not goal:
        raise HTTPException(status_code=404, detail="Goal not found")
    
    check_ins_count = db.query(DailyCheckIn).filter(DailyCheckIn.goal_id == goal_id).count()
    
    # Convert to dict and add check-ins count
    goal_dict = {
        "id": goal.id,
        "original_goal": goal.original_goal,
        "refined_goal": goal.refined_goal,
        "goal_category": goal.goal_category,
        "current_day": goal.current_day,
        "status": goal.status,
        "daily_tasks": goal.daily_tasks,
        "milestones": goal.milestones,
        "created_at": goal.created_at,
        "started_at": goal.started_at,
        "clarification_qa": goal.clarification_qa,
        "user_context": goal.user_context,
        "check_ins_count": check_ins_count
    }
    
    return goal_dict


# ============= Check-In Routes =============

@router.post("/goals/{goal_id}/check-in", response_model=CheckInResponse)
def daily_check_in(
    goal_id: int,
    check_in_data: CheckInCreate,
    request: Request,
    db: Session = Depends(get_db)
):
    """Submit daily check-in and get agent feedback."""
    # Get goal - verify session for privacy
    session_id = get_session_id(request)
    goal = db.query(Goal).filter(Goal.id == goal_id, Goal.session_id == session_id).first()
    if not goal:
        raise HTTPException(status_code=404, detail="Goal not found")
    
    if goal.status != "active":
        raise HTTPException(status_code=400, detail="Goal is not active")
    
    # Increment day
    goal.current_day += 1
    current_day = goal.current_day
    
    if current_day > 30:
        raise HTTPException(status_code=400, detail="Goal already completed (30 days)")
    
    # Get today's task
    today_task = {}
    if goal.daily_tasks:
        for task in goal.daily_tasks:
            if task.get("day") == current_day:
                today_task = task
                break
    
    # Get recent check-ins for context
    recent_check_ins = db.query(DailyCheckIn).filter(
        DailyCheckIn.goal_id == goal_id
    ).order_by(DailyCheckIn.day_number.desc()).limit(5).all()
    
    recent_check_ins_data = [
        {
            "day_number": ci.day_number,
            "task_completed": ci.task_completed,
            "confidence_level": ci.confidence_level
        }
        for ci in recent_check_ins
    ]
    
    # Run check-in agent
    agent_result = checkin_agent(
        goal=goal.refined_goal or goal.original_goal,
        day_number=current_day,
        today_task=today_task,
        task_completed=check_in_data.task_completed,
        user_response=check_in_data.user_response,
        obstacles=check_in_data.obstacles,
        confidence_level=check_in_data.confidence_level,
        recent_check_ins=recent_check_ins_data
    )
    
    # Create check-in record
    new_check_in = DailyCheckIn(
        goal_id=goal_id,
        day_number=current_day,
        task_completed=check_in_data.task_completed,
        user_response=check_in_data.user_response,
        obstacles=check_in_data.obstacles,
        confidence_level=check_in_data.confidence_level,
        agent_feedback=agent_result["feedback"],
        adjusted_plan=agent_result.get("adjusted_plan")
    )
    db.add(new_check_in)
    
    # Mark goal as completed if day 30
    if current_day == 30:
        goal.status = "completed"
        goal.completed = True
        goal.completed_at = datetime.utcnow()
    
    db.commit()
    db.refresh(new_check_in)
    
    return new_check_in


@router.get("/goals/{goal_id}/progress", response_model=ProgressSummary)
def get_progress(
    goal_id: int,
    request: Request,
    db: Session = Depends(get_db)
):
    """Get progress summary for a goal."""
    session_id = get_session_id(request)
    goal = db.query(Goal).filter(Goal.id == goal_id, Goal.session_id == session_id).first()
    if not goal:
        raise HTTPException(status_code=404, detail="Goal not found")
    
    # Get check-ins
    check_ins = db.query(DailyCheckIn).filter(DailyCheckIn.goal_id == goal_id).all()
    tasks_completed = sum(1 for ci in check_ins if ci.task_completed)
    
    # Calculate streak
    streak = 0
    for ci in sorted(check_ins, key=lambda x: x.day_number, reverse=True):
        if ci.task_completed:
            streak += 1
        else:
            break
    
    # Find next milestone
    next_milestone = None
    if goal.milestones:
        for milestone_day in [7, 14, 21, 30]:
            if goal.current_day < milestone_day:
                next_milestone = {
                    "day": milestone_day,
                    "description": goal.milestones.get(f"day_{milestone_day}", "")
                }
                break
    
    completion_rate = (tasks_completed / max(goal.current_day, 1)) * 100 if goal.current_day > 0 else 0
    
    return ProgressSummary(
        goal_id=goal.id,
        current_day=goal.current_day,
        total_days=30,
        tasks_completed=tasks_completed,
        tasks_remaining=30 - goal.current_day,
        completion_rate=round(completion_rate, 1),
        check_in_streak=streak,
        status=goal.status,
        next_milestone=next_milestone
    )


@router.get("/goals/{goal_id}/check-ins", response_model=List[CheckInResponse])
def get_check_ins(
    goal_id: int,
    request: Request,
    db: Session = Depends(get_db)
):
    """Get all check-ins for a goal."""
    session_id = get_session_id(request)
    goal = db.query(Goal).filter(Goal.id == goal_id, Goal.session_id == session_id).first()
    if not goal:
        raise HTTPException(status_code=404, detail="Goal not found")
    
    check_ins = db.query(DailyCheckIn).filter(
        DailyCheckIn.goal_id == goal_id
    ).order_by(DailyCheckIn.day_number).all()
    
    return check_ins

