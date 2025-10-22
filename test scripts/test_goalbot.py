"""Test script for GoalBot API endpoints."""

import requests
import time
from typing import Dict, Any

# Configuration
API_BASE_URL = 'http://localhost:8000/api/goalbot'
TEST_USER = {
    'username': 'test_user',
    'email': f'test_{int(time.time())}@example.com',  # Unique email
    'password': 'testpassword123'
}


def test_signup() -> str:
    """Test user signup and return auth token."""
    print("\n🔐 Testing Signup...")
    response = requests.post(
        f'{API_BASE_URL}/signup',
        json=TEST_USER
    )
    
    if response.status_code == 201:
        data = response.json()
        token = data['access_token']
        print(f"✓ Signup successful! Token: {token[:20]}...")
        return token
    else:
        print(f"✗ Signup failed: {response.status_code} - {response.text}")
        return None


def test_login() -> str:
    """Test user login and return auth token."""
    print("\n🔐 Testing Login...")
    response = requests.post(
        f'{API_BASE_URL}/login',
        json={
            'email': TEST_USER['email'],
            'password': TEST_USER['password']
        }
    )
    
    if response.status_code == 200:
        data = response.json()
        token = data['access_token']
        print(f"✓ Login successful! Token: {token[:20]}...")
        return token
    else:
        print(f"✗ Login failed: {response.status_code} - {response.text}")
        return None


def test_create_goal(token: str) -> Dict[str, Any]:
    """Test goal creation with clarification questions."""
    print("\n🎯 Testing Goal Creation...")
    response = requests.post(
        f'{API_BASE_URL}/goals/create',
        headers={'Authorization': f'Bearer {token}'},
        json={'goal': 'I want to learn Python programming'}
    )
    
    if response.status_code == 201:
        data = response.json()
        print(f"✓ Goal created! ID: {data['goal_id']}")
        print(f"  Clarification questions: {len(data['questions'])}")
        for q in data['questions']:
            print(f"    - {q['question']}")
        return data
    else:
        print(f"✗ Goal creation failed: {response.status_code} - {response.text}")
        return None


def test_clarification(token: str, goal_id: int, questions: list) -> Dict[str, Any]:
    """Test submitting clarification answers."""
    print("\n💬 Testing Clarification Submission...")
    
    # Prepare answers
    answers = {}
    for q in questions:
        qid = q['question_id']
        if 'current state' in q['question'].lower():
            answers[qid] = "I'm a complete beginner with no programming experience"
        elif 'success' in q['question'].lower():
            answers[qid] = "I want to build simple web scrapers and automate tasks"
        elif 'why' in q['question'].lower() or 'important' in q['question'].lower():
            answers[qid] = "I want to advance my career and automate repetitive work"
        elif 'time' in q['question'].lower():
            answers[qid] = "I can dedicate 1-2 hours daily"
        else:
            answers[qid] = "I'm motivated and ready to commit"
    
    response = requests.post(
        f'{API_BASE_URL}/goals/{goal_id}/clarify',
        headers={'Authorization': f'Bearer {token}'},
        json={'answers': answers}
    )
    
    if response.status_code == 200:
        data = response.json()
        print(f"✓ Clarification submitted!")
        print(f"  Original: {data['original_goal']}")
        print(f"  Refined: {data['refined_goal']}")
        print(f"  Category: {data['goal_category']}")
        print(f"  Achievable in 30 days: {data['is_achievable_in_30_days']}")
        return data
    else:
        print(f"✗ Clarification failed: {response.status_code} - {response.text}")
        return None


def test_breakdown(token: str, goal_id: int) -> Dict[str, Any]:
    """Test 30-day breakdown generation."""
    print("\n📋 Testing Breakdown Generation...")
    response = requests.post(
        f'{API_BASE_URL}/goals/{goal_id}/breakdown',
        headers={'Authorization': f'Bearer {token}'}
    )
    
    if response.status_code == 200:
        data = response.json()
        print(f"✓ Breakdown generated!")
        print(f"  Total daily tasks: {len(data['daily_tasks'])}")
        print(f"  Day 1 task: {data['daily_tasks'][0]['task']}")
        print(f"  Milestones: {list(data['milestones'].keys())}")
        return data
    else:
        print(f"✗ Breakdown failed: {response.status_code} - {response.text}")
        return None


def test_list_goals(token: str):
    """Test listing user's goals."""
    print("\n📝 Testing List Goals...")
    response = requests.get(
        f'{API_BASE_URL}/goals',
        headers={'Authorization': f'Bearer {token}'}
    )
    
    if response.status_code == 200:
        data = response.json()
        print(f"✓ Goals retrieved: {len(data)} goal(s)")
        for goal in data:
            print(f"  - {goal['refined_goal'] or goal['original_goal']} (Status: {goal['status']})")
    else:
        print(f"✗ List goals failed: {response.status_code} - {response.text}")


def test_get_goal_detail(token: str, goal_id: int):
    """Test getting detailed goal information."""
    print("\n🔍 Testing Get Goal Detail...")
    response = requests.get(
        f'{API_BASE_URL}/goals/{goal_id}',
        headers={'Authorization': f'Bearer {token}'}
    )
    
    if response.status_code == 200:
        data = response.json()
        print(f"✓ Goal details retrieved!")
        print(f"  ID: {data['id']}")
        print(f"  Status: {data['status']}")
        print(f"  Current day: {data['current_day']}/30")
        print(f"  Check-ins: {data['check_ins_count']}")
    else:
        print(f"✗ Get goal detail failed: {response.status_code} - {response.text}")


def test_check_in(token: str, goal_id: int, day: int = 1):
    """Test daily check-in submission."""
    print(f"\n✅ Testing Check-In (Day {day})...")
    response = requests.post(
        f'{API_BASE_URL}/goals/{goal_id}/check-in',
        headers={'Authorization': f'Bearer {token}'},
        json={
            'task_completed': True,
            'user_response': 'I completed today\'s task! Set up my Python environment and wrote my first Hello World program.',
            'obstacles': None,
            'confidence_level': 4
        }
    )
    
    if response.status_code == 200:
        data = response.json()
        print(f"✓ Check-in submitted!")
        print(f"  Day: {data['day_number']}")
        print(f"  Task completed: {data['task_completed']}")
        print(f"  Agent feedback: {data['agent_feedback'][:100]}...")
    else:
        print(f"✗ Check-in failed: {response.status_code} - {response.text}")


def test_progress(token: str, goal_id: int):
    """Test getting progress summary."""
    print("\n📊 Testing Progress Summary...")
    response = requests.get(
        f'{API_BASE_URL}/goals/{goal_id}/progress',
        headers={'Authorization': f'Bearer {token}'}
    )
    
    if response.status_code == 200:
        data = response.json()
        print(f"✓ Progress retrieved!")
        print(f"  Current day: {data['current_day']}/{data['total_days']}")
        print(f"  Tasks completed: {data['tasks_completed']}")
        print(f"  Completion rate: {data['completion_rate']}%")
        print(f"  Check-in streak: {data['check_in_streak']} days")
    else:
        print(f"✗ Progress failed: {response.status_code} - {response.text}")


def run_full_test():
    """Run complete GoalBot workflow test."""
    print("=" * 60)
    print("🚀 GoalBot API Test Suite")
    print("=" * 60)
    
    # Test authentication
    token = test_signup()
    if not token:
        print("\n❌ Test suite failed at signup")
        return
    
    # Test login (with existing user)
    token = test_login()
    if not token:
        print("\n❌ Test suite failed at login")
        return
    
    # Test goal creation workflow
    goal_data = test_create_goal(token)
    if not goal_data:
        print("\n❌ Test suite failed at goal creation")
        return
    
    goal_id = goal_data['goal_id']
    questions = goal_data['questions']
    
    # Test clarification
    refined_data = test_clarification(token, goal_id, questions)
    if not refined_data:
        print("\n❌ Test suite failed at clarification")
        return
    
    # Test breakdown
    breakdown_data = test_breakdown(token, goal_id)
    if not breakdown_data:
        print("\n❌ Test suite failed at breakdown")
        return
    
    # Test goal retrieval
    test_list_goals(token)
    test_get_goal_detail(token, goal_id)
    
    # Test check-in
    test_check_in(token, goal_id, day=1)
    
    # Test progress
    test_progress(token, goal_id)
    
    print("\n" + "=" * 60)
    print("✅ All tests completed successfully!")
    print("=" * 60)


if __name__ == '__main__':
    try:
        run_full_test()
    except requests.exceptions.ConnectionError:
        print("\n❌ Error: Cannot connect to API server")
        print("   Make sure the server is running on http://localhost:8000")
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()

