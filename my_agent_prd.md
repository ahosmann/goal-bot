# GoalBot: 30-Day Goal Achievement Agent - PRD

## Product Overview
GoalBot is an AI-powered goal achievement agent that transforms vague aspirations into actionable 30-day plans. Unlike passive tracking apps, GoalBot actively guides users through goal clarification, intelligently scopes ambitions into achievable 30-day sprints, breaks them into daily tasks, and provides contextual daily check-ins to maintain momentum and accountability.

**Core Value Proposition**: Turn any goal into a 30-day achievement through AI-guided refinement, daily breakdowns, and intelligent accountability.

## Onboarding Experience

**Initial Prompt**: "What do you want to work on over the next 30 days?"

**Goal Input Options**:

*Option 1: Popular Goal Templates* (quick-select buttons)
- 💧 Drink more water (8 glasses daily)
- 👥 Improve friendships (weekly meaningful connections)
- 📱 Decrease screen time (reduce by 30%)
- 🍳 Cook more meals (4+ home-cooked meals/week)
- 📚 Read more books (finish 2 books in 30 days)
- 🏃 Daily exercise (30 min movement/day)
- 🧘 Start meditation practice (10 min daily)
- 💤 Better sleep routine (7-8 hours consistently)

*Option 2: Custom Goal*
- Free-text input for user's own goal
- Placeholder: "Type your goal here"

**User Experience**: Templates auto-populate the goal field when clicked, but remain editable. Users can also skip templates and type custom goals directly.

**Benefits**: Reduces decision paralysis, provides goal inspiration, demonstrates what's achievable in 30 days, while maintaining flexibility for custom goals.

## User Journey
1. **Onboarding**: User selects popular goal template or enters custom goal ("Learn Spanish", "Get fit", "Launch side project")
2. **Clarification Session**: GoalBot asks up to 3 personalized, context-specific questions based on what user said, acting as a life coach mentor digging deeper into their specific situation
3. **Goal Confirmation**: Agent refines the goal into a SMART, achievable 30-day version and presents it as a question: "Is this the goal you'd like to set for the next 30 days?" (e.g., "Learn Spanish" → "Complete basic conversational Spanish and hold a 5-minute conversation")
4. **Weekly Breakdown with Challenge**: GoalBot presents structured 4-week mini-goals that build progressively toward the 30-day goal, plus detailed tasks for Days 1-7, ending with "Do you accept this challenge?" User can accept or request modifications
5. **Collaborative Refinement**: Throughout the process, GoalBot acts as mentor/coach, helping user shape goals through dialogue. User can suggest alternatives at any stage until plan feels authentic and achievable
6. **Daily Check-ins**: Each day, user receives an in-app prompt to log progress, answer reflection questions, and receive encouragement/adjustments
7. **Completion & Renewal**: At day 30, celebrate completion and optionally set the next 30-day sprint

## Core Features

### 1. Intelligent Goal Clarification
- **Context-aware questioning**: Questions tailored to user's specific goal, not generic template
- **Life coach approach**: Ask follow-up questions that dig deeper into what user said
- Examples of personalized clarification:
  - "Improve relationships" → Ask about specific relationships (family, friends, romantic)
  - "Exercise more" → Ask about current activity level and starting point (sedentary vs. already walking)
  - "Eat healthier" → Ask about specific foods to increase/decrease
  - "Learn a skill" → Ask about prior experience and learning style preferences
- Identifies if goal is too broad/narrow for 30 days
- Validates motivation and commitment level

### 2. 30-Day Goal Refinement
- Scopes overly ambitious goals into achievable 30-day milestones
- Applies SMART criteria (Specific, Measurable, Achievable, Relevant, Time-bound)
- Suggests realistic expectations based on goal category

### 3. Adaptive Daily Breakdown
- Creates 30 daily tasks with clear success criteria
- Sets weekly milestones (days 7, 14, 21, 30)
- Adjusts remaining plan based on actual progress

### 4. Daily Check-In System
- In-app chat notification at user-preferred time
- Contextual questions: "Did you complete today's task?", "What obstacles did you face?", "How confident are you about tomorrow?"
- Progress visualization and encouraging feedback
- Detects falling behind and suggests recovery plans

## User Experience & Interface

### Typing Indicators
- Display animated dots ("...") while GoalBot processes responses
- Shown during: clarifying question generation, goal refinement, weekly plan creation
- Provides visual feedback that agent is "thinking" and crafting response

### Conversation Flow Design

**Clarifying Questions** (Max 3 per message):
- Questions must be personalized to user's specific goal statement
- Act as life coach: probe deeper into what user shared, not generic templates
- All questions presented in single cohesive message, not separate bubbles

**Examples of Contextual Questioning**:

Goal: "I want to improve my relationships"
→ "Let's explore this together. Is there a specific relationship you want to focus on—like a friendship, family connection, or romantic relationship? And what would 'improved' look like to you?"

Goal: "I want to exercise more"  
→ "I'd like to understand where you're starting from. How active are you currently—mostly sedentary, or already doing some walking? Would you prefer starting with something gentle like daily walks, or are you ready for more structured workouts?"

Goal: "I want to eat healthier"
→ "What specific changes are you thinking about? Are there certain foods you'd like to eat more of (like vegetables or home-cooked meals), or things you want to cut back on (like fast food or sugar)?"

Goal: "I want to be more productive"
→ "Help me understand what's getting in your way right now. Is it procrastination, too many distractions, or feeling overwhelmed by too many tasks? And which area of life needs this most—work, personal projects, or home?"

**Goal Confirmation**:
- Refined goal presented as question format requiring user approval
- Format: "Based on what you've shared, I suggest: [refined goal]. Is this the goal you'd like to set for the next 30 days?"
- User can accept, reject, or request modifications

**Weekly Plan Presentation**:
```
Week 1: [Foundation mini-goal - establish baseline]
Week 2: [Building mini-goal - develop consistency]  
Week 3: [Advancing mini-goal - increase challenge]
Week 4: [Achievement - reach 30-day goal]

Day 1: [Specific actionable task with success criteria]
Day 2: [Specific actionable task with success criteria]
Day 3: [Specific actionable task with success criteria]
Day 4: [Specific actionable task with success criteria]
Day 5: [Specific actionable task with success criteria]
Day 6: [Specific actionable task with success criteria]
Day 7: [Specific actionable task with success criteria]

Do you accept this challenge?
```

**Example - "Read 2 books in 30 days"**:
```
Week 1: Foundation - Choose first book and establish reading habit (complete 50 pages)
Week 2: Development - Finish first book and build reading stamina (complete remaining 150+ pages)
Week 3: Advancement - Start second book with increased pace (read 120 pages)
Week 4: Achievement - Complete second book and reflect on both (finish final 80 pages + write reflections)

Day 1: Select first book based on interests, read Chapter 1 (15-20 pages), find ideal reading spot
Day 2: Read 15-20 pages, note what captures your attention
Day 3: Read 15-20 pages at preferred time of day
Day 4: Read 15-20 pages, try different reading location
Day 5: Read 15-20 pages, reflect on story so far
Day 6: Read 15-20 pages at consistent time
Day 7: Complete Week 1 goal (50 pages total), adjust pace if needed

Do you accept this challenge?
```

### Project Management Approach

GoalBot applies professional project management skills to break down 30-day goals into progressive milestones:

**Progressive Milestone Design**:
- Each weekly milestone must build upon the previous week
- Week 1: Foundation (establish baseline, learn fundamentals)
- Week 2: Development (build consistency, increase capacity)  
- Week 3: Advancement (push beyond comfort zone, add complexity)
- Week 4: Achievement (reach stretch goal, demonstrate mastery)

**Anti-Pattern - Avoid Repetitive Milestones**:
❌ Week 1: Exercise 3 times
❌ Week 2: Exercise 3 times  
❌ Week 3: Exercise 3 times
❌ Week 4: Exercise 3 times

**Correct Pattern - Progressive Milestones**:
✓ Week 1: Establish habit (3 x 20-min walks)
✓ Week 2: Build endurance (3 x 30-min walks at faster pace)
✓ Week 3: Add variety (2 walks + 1 beginner strength session)  
✓ Week 4: Achieve goal (4 x 30-min mixed cardio/strength workouts)

**Milestone Characteristics**:
- Each milestone is meaningful checkpoint toward end goal
- Clear differentiation between weeks (not just repetition)
- Builds skills/capacity needed for subsequent milestones
- Weekly goals form logical progression story

### Collaborative Goal Setting
- GoalBot acts as mentor/personal trainer/life coach helping shape goals
- User retains control: can request modifications, suggest alternatives at any stage
- Goal must feel like user's authentic commitment, not imposed plan
- Iterative refinement until user genuinely wants to "sign up" for the 30-day sprint
- Language emphasizes partnership: "Let's adjust...", "What if we...", "How does this feel?"

## Accessibility & Inclusivity

### Achievability Standards
- All suggested goals achievable for average USA adult with typical constraints
- Plans account for realistic time (work, family, commute, life responsibilities)
- No assumptions about: physical ability, financial resources, living situation, schedule flexibility
- Default: 30-60 min/day time commitment unless user specifies more

### Accommodations & Adaptations
- Users can request modifications for disabilities, chronic conditions, or special circumstances
- ADA-friendly approach: alternative activities, accessible formats, flexible timing
- Adaptive suggestions when standard approaches don't fit user's situation
- Example: Physical fitness goal → offer seated exercises, chair yoga, adaptive movement options

### Inclusive Design Principles
- Gender-neutral language (avoid "guys", "chairman", gendered fitness standards)
- Culturally sensitive (no assumptions about holidays, diet, family structure)
- Socioeconomically inclusive (no required purchases, gym memberships, expensive equipment)
- Accessible to diverse abilities, backgrounds, and circumstances

## Safety & Risk Management

### Medical Advice Prohibition
- **GoalBot never provides medical, mental health, or clinical advice**
- Health-related goals: "Please consult your healthcare provider before starting any new health program"
- Mental health goals: Suggest professional support, provide 988 resource
- Nutrition/diet goals: Recommend registered dietitian consultation

### Unsafe Goal Detection & Intervention
If goal appears physically impossible, unhealthy, or ill-advised:
1. **Ask clarifying questions** to understand user's true intent
2. **Explain concerns professionally** without judgment
3. **Suggest safer, achievable alternative** that addresses underlying motivation

Examples:
- "Lose 30 pounds in 30 days" → "I want to help you reach a healthy weight safely. Rapid weight loss can be harmful. Would you be open to a goal of developing sustainable healthy habits this month?"
- "Stop sleeping to be more productive" → "I'm concerned this could harm your health. Quality sleep improves productivity. What if we focused on optimizing your waking hours instead?"

**Principle**: Goals must never risk user health or safety.

### Crisis Intervention Protocol

**Trigger phrases**: self-harm, suicide, "want to die", "end it all", "no reason to live", severe depression language

**Immediate Response**:
1. Stop goal-setting conversation immediately
2. Express concern with empathy (no clinical assessment or advice)
3. Provide crisis resources prominently

**Template Response**:
"I'm concerned about what you've shared. Please reach out to a trained crisis counselor who can provide immediate support. You can call or text **988** (available 24/7) or visit [988lifeline.org](https://988lifeline.org/). Your safety is the priority."

**Follow-up**: Do not continue goal-setting until user indicates they've received appropriate support or explicitly wants to continue with a different topic.

**Important**: GoalBot acknowledges but does not diagnose, counsel, or attempt to resolve crisis situations. Always defer to professional crisis intervention.

## Architecture

**Multi-Agent System** (adapting existing LangGraph trip-planner architecture):

- **Clarification Agent**: Conducts goal intake, acts as life coach mentor, asks up to 3 personalized, context-specific questions based on user's goal (single message), probes deeper into their specific situation rather than using generic question templates, validates goal feasibility, **detects safety concerns and crisis language**
- **Refinement Agent**: Scopes goal to 30 days, applies SMART framework, presents as confirmation question ("Is this the goal you'd like to set?"), **validates safety/achievability against health risks**, suggests modifications collaboratively
- **Breakdown Agent**: Applies project management methodology to create 4 weekly mini-goals that build progressively with clear differentiation between weeks (foundation → development → advancement → achievement), ensuring each milestone advances toward the goal rather than repeating + detailed daily tasks for Days 1-7, ends with "Do you accept this challenge?", accommodates user modification requests
- **Check-In Agent**: Daily progress tracking, motivational messaging, adaptive replanning, **monitors for crisis language in responses**, maintains safety protocols

**LangGraph Orchestration**: Sequential flow (Clarification → Refinement → Breakdown), with Check-In Agent invoked daily

**RAG System**: Vector database of goal templates, success patterns, motivational content, and domain-specific advice (fitness, learning, career, creativity)

**State Management**: 
- User profiles with authentication (session_id, user_id already implemented)
- Goal state tracking (current day, completion status, task history)
- 30-day persistence with historical archive

## Technical Requirements

**Backend** (FastAPI):
- User authentication endpoints (`/signup`, `/login`)
- Goal management (`/goals/create`, `/goals/{id}/check-in`, `/goals/{id}/progress`)
- Daily notification scheduler (cron job or task queue)
- Progress analytics endpoint

**Database**:
- User profiles, goal records, daily check-in logs
- PostgreSQL or similar with 30-day active goals + historical archive

**Frontend**:
- Chat interface for goal setup and daily check-ins
- **Typing indicator component** (animated dots shown during agent processing)
- **Formatted message display** for weekly breakdown structure (preserves formatting, line breaks)
- **Crisis resource display** (prominent 988 link display when safety protocol triggered)
- Progress dashboard with 30-day calendar view
- Notification system for daily prompts

**Integrations**:
- OpenAI/LLM provider (already configured)
- Notification service (in-app initially, email/SMS future)
- Arize observability for agent performance tracking

## Success Metrics

**Primary**:
- Goal completion rate (% of users completing 30-day sprints)
- Daily check-in adherence (target: 80%+ daily response rate)

**Secondary**:
- Time to first goal submission (target: < 60 seconds for template users)
- Time to goal refinement (< 5 minutes clarification session)
- User retention (% starting second 30-day sprint)
- Average days to abandonment (track drop-off patterns)
- Template vs. custom goal ratio (understand user preferences)
- **User modifications requested per goal** (track collaborative refinement engagement)
- **Accommodation requests handled successfully** (disability/special needs adaptations)

**Qualitative**:
- User satisfaction scores post-completion
- Quality of daily task breakdowns (manual review sample)

**Safety & Compliance**:
- **Safety trigger accuracy** (manual review of crisis/health concern detections - target 95%+ precision)
- False positive rate for crisis intervention (minimize unnecessary interruptions)
- Time to crisis resource display (< 2 seconds when triggered)

## Timeline

**Phase 1 (Weeks 1-3)**: MVP Core
- Onboarding flow with 8 popular goal templates
- Adapt trip-planner agents to goal domain
- Build goal clarification, refinement, and breakdown flows
- User authentication and goal state persistence
- Basic daily check-in (manual trigger)

**Phase 2 (Weeks 4-5)**: Daily Check-In Automation
- Implement scheduled daily notifications
- Progress tracking dashboard
- Adaptive replanning based on progress

**Phase 3 (Week 6+)**: Enhancement
- RAG system with goal templates and best practices
- Analytics dashboard
- Mobile-optimized interface
- Beta launch with 50-100 users

**Success Criteria for Launch**: 70%+ goal completion rate and 75%+ daily check-in adherence among beta users.

