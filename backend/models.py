"""Database models for GoalBot."""

from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Boolean, JSON
from sqlalchemy.orm import relationship
from datetime import datetime
from database import Base


class User(Base):
    """User account model."""
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    username = Column(String(100), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    is_active = Column(Boolean, default=True)
    
    # Relationships
    goals = relationship("Goal", back_populates="user", cascade="all, delete-orphan")


class Goal(Base):
    """30-day goal model."""
    __tablename__ = "goals"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    session_id = Column(String(255), index=True, nullable=True)  # Device-specific session for MVP privacy
    
    # Goal content
    original_goal = Column(Text, nullable=False)  # User's initial input
    refined_goal = Column(Text)  # SMART goal after refinement
    goal_category = Column(String(100))  # fitness, learning, career, creativity, etc.
    
    # Clarification data
    clarification_qa = Column(JSON)  # Questions and answers from clarification session
    user_context = Column(JSON)  # Current state, resources, constraints
    
    # Goal breakdown
    daily_tasks = Column(JSON)  # Array of 30 daily tasks
    milestones = Column(JSON)  # Days 7, 14, 21, 30 milestone descriptions
    
    # Status tracking
    current_day = Column(Integer, default=0)  # 0-30
    status = Column(String(50), default="clarifying")  # clarifying, active, completed, abandoned
    completed = Column(Boolean, default=False)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    started_at = Column(DateTime)  # When daily tracking begins
    completed_at = Column(DateTime)
    
    # Relationships
    user = relationship("User", back_populates="goals")
    check_ins = relationship("DailyCheckIn", back_populates="goal", cascade="all, delete-orphan")


class DailyCheckIn(Base):
    """Daily progress check-in model."""
    __tablename__ = "daily_check_ins"
    
    id = Column(Integer, primary_key=True, index=True)
    goal_id = Column(Integer, ForeignKey("goals.id"), nullable=False)
    day_number = Column(Integer, nullable=False)  # 1-30
    
    # Check-in data
    task_completed = Column(Boolean)
    user_response = Column(Text)  # Free-form response about progress
    obstacles = Column(Text)  # What challenges did they face?
    confidence_level = Column(Integer)  # 1-5 scale for tomorrow
    
    # Agent feedback
    agent_feedback = Column(Text)  # Encouragement and guidance from Check-In Agent
    adjusted_plan = Column(JSON)  # Any modifications to remaining tasks
    
    # Timestamp
    checked_in_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    goal = relationship("Goal", back_populates="check_ins")
    
    class Config:
        # Ensure day_number is unique per goal
        __table_args__ = (
            {"sqlite_autoincrement": True},
        )

