"""Pydantic schemas for GoalBot API."""

from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List, Dict, Any
from datetime import datetime


# ============= Authentication Schemas =============

class UserSignup(BaseModel):
    email: EmailStr
    username: str = Field(..., min_length=3, max_length=50)
    password: str = Field(..., min_length=8)


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class UserResponse(BaseModel):
    id: int
    email: str
    username: str
    created_at: datetime
    
    class Config:
        from_attributes = True


# ============= Goal Schemas =============

class GoalCreate(BaseModel):
    """Initial goal submission by user."""
    goal: str = Field(..., min_length=10, max_length=500, description="The user's goal statement")


class ClarificationResponse(BaseModel):
    """User's responses to clarification questions."""
    answers: Dict[str, str] = Field(..., description="Question ID to answer mapping")


class GoalResponse(BaseModel):
    """Goal information returned to user."""
    id: int
    original_goal: str
    refined_goal: Optional[str]
    goal_category: Optional[str]
    current_day: int
    status: str
    daily_tasks: Optional[List[Dict[str, Any]]]
    milestones: Optional[Dict[str, str]]
    created_at: datetime
    started_at: Optional[datetime]
    
    class Config:
        from_attributes = True


class GoalDetail(GoalResponse):
    """Detailed goal view including clarification data."""
    clarification_qa: Optional[Dict[str, Any]]
    user_context: Optional[Dict[str, Any]]
    check_ins_count: int = 0


# ============= Check-In Schemas =============

class CheckInCreate(BaseModel):
    """Daily check-in submission."""
    task_completed: bool
    user_response: str = Field(..., min_length=10, max_length=1000)
    obstacles: Optional[str] = Field(None, max_length=500)
    confidence_level: int = Field(..., ge=1, le=5, description="Confidence for tomorrow (1-5)")


class CheckInResponse(BaseModel):
    """Check-in response with agent feedback."""
    id: int
    day_number: int
    task_completed: bool
    user_response: str
    obstacles: Optional[str]
    confidence_level: int
    agent_feedback: str
    adjusted_plan: Optional[Dict[str, Any]]
    checked_in_at: datetime
    
    class Config:
        from_attributes = True


# ============= Agent Workflow Schemas =============

class ClarificationQuestion(BaseModel):
    """A clarification question from the agent."""
    question_id: str
    question: str
    hint: Optional[str] = None


class ClarificationSession(BaseModel):
    """Clarification session with questions."""
    goal_id: int
    questions: List[ClarificationQuestion]
    message: str = "Let's clarify your goal with a few questions:"


class RefinedGoalResult(BaseModel):
    """Result after goal refinement."""
    goal_id: int
    original_goal: str
    refined_goal: str
    goal_category: str
    reasoning: str
    is_achievable_in_30_days: bool


class DailyTask(BaseModel):
    """A single daily task."""
    day: int
    task: str
    success_criteria: str
    estimated_time: str


class GoalBreakdown(BaseModel):
    """Complete 30-day breakdown."""
    goal_id: int
    daily_tasks: List[DailyTask]
    milestones: Dict[str, str]  # day 7, 14, 21, 30
    message: str = "Your 30-day plan is ready!"


# ============= Progress Tracking Schemas =============

class ProgressSummary(BaseModel):
    """Overall progress summary for a goal."""
    goal_id: int
    current_day: int
    total_days: int = 30
    tasks_completed: int
    tasks_remaining: int
    completion_rate: float  # percentage
    check_in_streak: int  # consecutive days
    status: str
    next_milestone: Optional[Dict[str, Any]]

