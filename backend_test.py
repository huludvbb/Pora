"""
Backend test suite for Pro sub-app API endpoints.
Tests all /api/pro endpoints with authentication and edge cases.
"""

import requests
import json
from typing import Optional

# Base URL from frontend .env
BASE_URL = "https://d8b2b820-9fd7-4169-93af-78c5f896db15.preview.emergentagent.com/api"

# Test credentials
STUDENT_EMAIL = "mei@demo.com"
STUDENT_PASSWORD = "Demo1234!"
SECOND_USER_EMAIL = "diego@demo.com"
SECOND_USER_PASSWORD = "Demo1234!"


class TestResult:
    def __init__(self):
        self.passed = 0
        self.failed = 0
        self.errors = []
    
    def add_pass(self, test_name: str):
        self.passed += 1
        print(f"✅ PASS: {test_name}")
    
    def add_fail(self, test_name: str, error: str):
        self.failed += 1
        self.errors.append(f"{test_name}: {error}")
        print(f"❌ FAIL: {test_name}")
        print(f"   Error: {error}")
    
    def summary(self):
        total = self.passed + self.failed
        print(f"\n{'='*60}")
        print(f"TEST SUMMARY: {self.passed}/{total} passed")
        print(f"{'='*60}")
        if self.errors:
            print("\nFailed tests:")
            for error in self.errors:
                print(f"  - {error}")
        return self.failed == 0


def login(email: str, password: str) -> Optional[str]:
    """Login and return JWT token."""
    try:
        response = requests.post(
            f"{BASE_URL}/auth/login",
            json={"email": email, "password": password},
            timeout=10
        )
        if response.status_code == 200:
            return response.json().get("token")
        else:
            print(f"Login failed for {email}: {response.status_code} - {response.text}")
            return None
    except Exception as e:
        print(f"Login error for {email}: {e}")
        return None


def test_pro_endpoints():
    """Test all Pro sub-app endpoints."""
    result = TestResult()
    
    # Login as student user (mei)
    print("\n" + "="*60)
    print("LOGGING IN AS STUDENT USER (mei@demo.com)")
    print("="*60)
    mei_token = login(STUDENT_EMAIL, STUDENT_PASSWORD)
    if not mei_token:
        result.add_fail("Login mei@demo.com", "Failed to get token")
        return result
    result.add_pass("Login mei@demo.com")
    
    headers_mei = {"Authorization": f"Bearer {mei_token}"}
    
    # Login as second user (diego)
    print("\n" + "="*60)
    print("LOGGING IN AS SECOND USER (diego@demo.com)")
    print("="*60)
    diego_token = login(SECOND_USER_EMAIL, SECOND_USER_PASSWORD)
    if not diego_token:
        result.add_fail("Login diego@demo.com", "Failed to get token")
        return result
    result.add_pass("Login diego@demo.com")
    
    headers_diego = {"Authorization": f"Bearer {diego_token}"}
    
    # Test 1: GET /api/pro/me - auto-create profile and wallet
    print("\n" + "="*60)
    print("TEST 1: GET /api/pro/me (auto-create profile)")
    print("="*60)
    try:
        response = requests.get(f"{BASE_URL}/pro/me", headers=headers_mei, timeout=10)
        if response.status_code == 200:
            data = response.json()
            if "profile" in data and "wallet" in data:
                profile = data["profile"]
                wallet = data["wallet"]
                if (wallet.get("balance") == 60 and 
                    wallet.get("currency") == "MIN" and 
                    profile.get("role") == "student"):
                    result.add_pass("GET /api/pro/me - auto-create profile with wallet")
                    mei_profile_id = profile.get("id")
                else:
                    result.add_fail("GET /api/pro/me", f"Unexpected values: wallet={wallet}, role={profile.get('role')}")
            else:
                result.add_fail("GET /api/pro/me", f"Missing profile or wallet in response: {data}")
        else:
            result.add_fail("GET /api/pro/me", f"Status {response.status_code}: {response.text}")
    except Exception as e:
        result.add_fail("GET /api/pro/me", str(e))
    
    # Test 2: PUT /api/pro/me - update profile
    print("\n" + "="*60)
    print("TEST 2: PUT /api/pro/me (update profile)")
    print("="*60)
    try:
        update_data = {
            "bio": "Test bio for Pro app",
            "native_accent": "American",
            "teaches": ["en", "es"],
            "specialties": ["Business", "Conversation"],
            "languages": ["ja", "ko"],
            "hourly_rate": 25.5,
            "video_intro_url": "https://example.com/video.mp4"
        }
        response = requests.put(f"{BASE_URL}/pro/me", headers=headers_mei, json=update_data, timeout=10)
        if response.status_code == 200:
            data = response.json()
            if (data.get("bio") == update_data["bio"] and
                data.get("native_accent") == update_data["native_accent"] and
                data.get("hourly_rate") == update_data["hourly_rate"]):
                result.add_pass("PUT /api/pro/me - update and persist fields")
            else:
                result.add_fail("PUT /api/pro/me", f"Fields not updated correctly: {data}")
        else:
            result.add_fail("PUT /api/pro/me", f"Status {response.status_code}: {response.text}")
    except Exception as e:
        result.add_fail("PUT /api/pro/me", str(e))
    
    # Test 3: GET /api/pro/me again to verify persistence
    print("\n" + "="*60)
    print("TEST 3: GET /api/pro/me (verify persistence)")
    print("="*60)
    try:
        response = requests.get(f"{BASE_URL}/pro/me", headers=headers_mei, timeout=10)
        if response.status_code == 200:
            data = response.json()
            profile = data.get("profile", {})
            if (profile.get("bio") == "Test bio for Pro app" and
                profile.get("native_accent") == "American" and
                profile.get("hourly_rate") == 25.5):
                result.add_pass("GET /api/pro/me - verify persistence")
            else:
                result.add_fail("GET /api/pro/me persistence", f"Fields not persisted: {profile}")
        else:
            result.add_fail("GET /api/pro/me persistence", f"Status {response.status_code}: {response.text}")
    except Exception as e:
        result.add_fail("GET /api/pro/me persistence", str(e))
    
    # Test 4: POST /api/pro/role - change to tutor
    print("\n" + "="*60)
    print("TEST 4: POST /api/pro/role (change to tutor)")
    print("="*60)
    try:
        response = requests.post(f"{BASE_URL}/pro/role", headers=headers_mei, json={"role": "tutor"}, timeout=10)
        if response.status_code == 200:
            data = response.json()
            if data.get("role") == "tutor":
                result.add_pass("POST /api/pro/role - change to tutor")
            else:
                result.add_fail("POST /api/pro/role tutor", f"Role not changed: {data.get('role')}")
        else:
            result.add_fail("POST /api/pro/role tutor", f"Status {response.status_code}: {response.text}")
    except Exception as e:
        result.add_fail("POST /api/pro/role tutor", str(e))
    
    # Test 5: POST /api/pro/role - change back to student
    print("\n" + "="*60)
    print("TEST 5: POST /api/pro/role (change back to student)")
    print("="*60)
    try:
        response = requests.post(f"{BASE_URL}/pro/role", headers=headers_mei, json={"role": "student"}, timeout=10)
        if response.status_code == 200:
            data = response.json()
            if data.get("role") == "student":
                result.add_pass("POST /api/pro/role - change to student")
            else:
                result.add_fail("POST /api/pro/role student", f"Role not changed: {data.get('role')}")
        else:
            result.add_fail("POST /api/pro/role student", f"Status {response.status_code}: {response.text}")
    except Exception as e:
        result.add_fail("POST /api/pro/role student", str(e))
    
    # Test 6: POST /api/pro/role - invalid role (should 422)
    print("\n" + "="*60)
    print("TEST 6: POST /api/pro/role (invalid role - expect 422)")
    print("="*60)
    try:
        response = requests.post(f"{BASE_URL}/pro/role", headers=headers_mei, json={"role": "admin"}, timeout=10)
        if response.status_code == 422:
            result.add_pass("POST /api/pro/role - invalid role returns 422")
        else:
            result.add_fail("POST /api/pro/role invalid", f"Expected 422, got {response.status_code}")
    except Exception as e:
        result.add_fail("POST /api/pro/role invalid", str(e))
    
    # Test 7: GET /api/pro/tutors - list all tutors (should be 8)
    print("\n" + "="*60)
    print("TEST 7: GET /api/pro/tutors (list all - expect 8)")
    print("="*60)
    try:
        response = requests.get(f"{BASE_URL}/pro/tutors", timeout=10)
        if response.status_code == 200:
            tutors = response.json()
            if len(tutors) == 8:
                # Check sorting: featured and higher-rated first
                if tutors[0].get("featured") or tutors[0].get("rating", 0) >= 4.8:
                    result.add_pass("GET /api/pro/tutors - returns 8 tutors with correct sorting")
                else:
                    result.add_fail("GET /api/pro/tutors sorting", f"First tutor not featured/high-rated: {tutors[0]}")
            else:
                result.add_fail("GET /api/pro/tutors", f"Expected 8 tutors, got {len(tutors)}")
        else:
            result.add_fail("GET /api/pro/tutors", f"Status {response.status_code}: {response.text}")
    except Exception as e:
        result.add_fail("GET /api/pro/tutors", str(e))
    
    # Test 8: GET /api/pro/tutors?language=en - filter by language
    print("\n" + "="*60)
    print("TEST 8: GET /api/pro/tutors?language=en (filter English)")
    print("="*60)
    try:
        response = requests.get(f"{BASE_URL}/pro/tutors?language=en", timeout=10)
        if response.status_code == 200:
            tutors = response.json()
            if all("en" in t.get("teaches", []) for t in tutors):
                result.add_pass(f"GET /api/pro/tutors?language=en - returns only English tutors ({len(tutors)} found)")
            else:
                result.add_fail("GET /api/pro/tutors language filter", "Some tutors don't teach English")
        else:
            result.add_fail("GET /api/pro/tutors language filter", f"Status {response.status_code}: {response.text}")
    except Exception as e:
        result.add_fail("GET /api/pro/tutors language filter", str(e))
    
    # Test 9: GET /api/pro/tutors?q=business - search filter
    print("\n" + "="*60)
    print("TEST 9: GET /api/pro/tutors?q=business (search)")
    print("="*60)
    try:
        response = requests.get(f"{BASE_URL}/pro/tutors?q=business", timeout=10)
        if response.status_code == 200:
            tutors = response.json()
            if len(tutors) > 0:
                # Check if results contain "business" in name, bio, or specialties
                valid = all(
                    "business" in t.get("name", "").lower() or
                    "business" in t.get("bio", "").lower() or
                    any("business" in s.lower() for s in t.get("specialties", []))
                    for t in tutors
                )
                if valid:
                    result.add_pass(f"GET /api/pro/tutors?q=business - returns matching tutors ({len(tutors)} found)")
                else:
                    result.add_fail("GET /api/pro/tutors search", "Some results don't match search term")
            else:
                result.add_fail("GET /api/pro/tutors search", "No results found for 'business'")
        else:
            result.add_fail("GET /api/pro/tutors search", f"Status {response.status_code}: {response.text}")
    except Exception as e:
        result.add_fail("GET /api/pro/tutors search", str(e))
    
    # Test 10: GET /api/pro/tutors/{id} - get specific tutor
    print("\n" + "="*60)
    print("TEST 10: GET /api/pro/tutors/{id} (valid tutor)")
    print("="*60)
    try:
        # First get a tutor ID
        response = requests.get(f"{BASE_URL}/pro/tutors", timeout=10)
        if response.status_code == 200:
            tutors = response.json()
            if len(tutors) > 0:
                tutor_id = tutors[0]["id"]
                response = requests.get(f"{BASE_URL}/pro/tutors/{tutor_id}", timeout=10)
                if response.status_code == 200:
                    tutor = response.json()
                    if tutor.get("id") == tutor_id:
                        result.add_pass("GET /api/pro/tutors/{id} - returns tutor details")
                    else:
                        result.add_fail("GET /api/pro/tutors/{id}", f"Wrong tutor returned: {tutor.get('id')}")
                else:
                    result.add_fail("GET /api/pro/tutors/{id}", f"Status {response.status_code}: {response.text}")
            else:
                result.add_fail("GET /api/pro/tutors/{id}", "No tutors available to test")
        else:
            result.add_fail("GET /api/pro/tutors/{id}", "Failed to get tutor list")
    except Exception as e:
        result.add_fail("GET /api/pro/tutors/{id}", str(e))
    
    # Test 11: GET /api/pro/tutors/{id} - invalid ID (should 404)
    print("\n" + "="*60)
    print("TEST 11: GET /api/pro/tutors/{id} (invalid - expect 404)")
    print("="*60)
    try:
        response = requests.get(f"{BASE_URL}/pro/tutors/nonexistent-id-12345", timeout=10)
        if response.status_code == 404:
            result.add_pass("GET /api/pro/tutors/{invalid_id} - returns 404")
        else:
            result.add_fail("GET /api/pro/tutors/{invalid_id}", f"Expected 404, got {response.status_code}")
    except Exception as e:
        result.add_fail("GET /api/pro/tutors/{invalid_id}", str(e))
    
    # Test 12: POST /api/pro/match - instant match (no params)
    print("\n" + "="*60)
    print("TEST 12: POST /api/pro/match (instant match)")
    print("="*60)
    try:
        response = requests.post(f"{BASE_URL}/pro/match", headers=headers_mei, json={}, timeout=10)
        if response.status_code == 200:
            session = response.json()
            if (session.get("status") == "active" and
                session.get("stream_room_token") and
                session.get("tutor")):
                result.add_pass("POST /api/pro/match - instant match creates active session")
                mei_session_id = session.get("id")
            else:
                result.add_fail("POST /api/pro/match instant", f"Invalid session: {session}")
        else:
            result.add_fail("POST /api/pro/match instant", f"Status {response.status_code}: {response.text}")
    except Exception as e:
        result.add_fail("POST /api/pro/match instant", str(e))
    
    # Test 13: POST /api/pro/match - match with language filter
    print("\n" + "="*60)
    print("TEST 13: POST /api/pro/match (language=ja)")
    print("="*60)
    try:
        response = requests.post(f"{BASE_URL}/pro/match", headers=headers_mei, json={"language": "ja"}, timeout=10)
        if response.status_code == 200:
            session = response.json()
            tutor = session.get("tutor", {})
            if "ja" in tutor.get("teaches", []):
                result.add_pass("POST /api/pro/match language=ja - matches Japanese tutor")
            else:
                result.add_fail("POST /api/pro/match language", f"Tutor doesn't teach Japanese: {tutor.get('teaches')}")
        else:
            result.add_fail("POST /api/pro/match language", f"Status {response.status_code}: {response.text}")
    except Exception as e:
        result.add_fail("POST /api/pro/match language", str(e))
    
    # Test 14: POST /api/pro/match - match with specific tutor_id
    print("\n" + "="*60)
    print("TEST 14: POST /api/pro/match (specific tutor_id)")
    print("="*60)
    try:
        # Get a tutor ID first
        response = requests.get(f"{BASE_URL}/pro/tutors", timeout=10)
        if response.status_code == 200:
            tutors = response.json()
            if len(tutors) > 0:
                tutor_id = tutors[0]["id"]
                response = requests.post(f"{BASE_URL}/pro/match", headers=headers_mei, json={"tutor_id": tutor_id}, timeout=10)
                if response.status_code == 200:
                    session = response.json()
                    if session.get("tutor", {}).get("id") == tutor_id:
                        result.add_pass("POST /api/pro/match tutor_id - books specific tutor")
                    else:
                        result.add_fail("POST /api/pro/match tutor_id", f"Wrong tutor matched: {session.get('tutor', {}).get('id')}")
                else:
                    result.add_fail("POST /api/pro/match tutor_id", f"Status {response.status_code}: {response.text}")
            else:
                result.add_fail("POST /api/pro/match tutor_id", "No tutors available")
        else:
            result.add_fail("POST /api/pro/match tutor_id", "Failed to get tutor list")
    except Exception as e:
        result.add_fail("POST /api/pro/match tutor_id", str(e))
    
    # Test 15: POST /api/pro/match - nonexistent tutor_id (should 404)
    print("\n" + "="*60)
    print("TEST 15: POST /api/pro/match (nonexistent tutor - expect 404)")
    print("="*60)
    try:
        response = requests.post(f"{BASE_URL}/pro/match", headers=headers_mei, json={"tutor_id": "nonexistent"}, timeout=10)
        if response.status_code == 404:
            result.add_pass("POST /api/pro/match nonexistent tutor - returns 404")
        else:
            result.add_fail("POST /api/pro/match nonexistent", f"Expected 404, got {response.status_code}")
    except Exception as e:
        result.add_fail("POST /api/pro/match nonexistent", str(e))
    
    # Test 16: GET /api/pro/sessions - list user's sessions
    print("\n" + "="*60)
    print("TEST 16: GET /api/pro/sessions (list sessions)")
    print("="*60)
    try:
        response = requests.get(f"{BASE_URL}/pro/sessions", headers=headers_mei, timeout=10)
        if response.status_code == 200:
            sessions = response.json()
            if len(sessions) >= 1:  # Should have at least the sessions we created
                result.add_pass(f"GET /api/pro/sessions - returns sessions ({len(sessions)} found)")
                # Store a session ID for later tests
                test_session_id = sessions[0]["id"]
            else:
                result.add_fail("GET /api/pro/sessions", "No sessions found")
        else:
            result.add_fail("GET /api/pro/sessions", f"Status {response.status_code}: {response.text}")
    except Exception as e:
        result.add_fail("GET /api/pro/sessions", str(e))
    
    # Test 17: GET /api/pro/sessions/{id} - owner can fetch
    print("\n" + "="*60)
    print("TEST 17: GET /api/pro/sessions/{id} (owner access)")
    print("="*60)
    try:
        response = requests.get(f"{BASE_URL}/pro/sessions", headers=headers_mei, timeout=10)
        if response.status_code == 200:
            sessions = response.json()
            if len(sessions) > 0:
                session_id = sessions[0]["id"]
                response = requests.get(f"{BASE_URL}/pro/sessions/{session_id}", headers=headers_mei, timeout=10)
                if response.status_code == 200:
                    session = response.json()
                    if session.get("id") == session_id:
                        result.add_pass("GET /api/pro/sessions/{id} - owner can fetch")
                    else:
                        result.add_fail("GET /api/pro/sessions/{id} owner", f"Wrong session: {session.get('id')}")
                else:
                    result.add_fail("GET /api/pro/sessions/{id} owner", f"Status {response.status_code}: {response.text}")
            else:
                result.add_fail("GET /api/pro/sessions/{id} owner", "No sessions to test")
        else:
            result.add_fail("GET /api/pro/sessions/{id} owner", "Failed to get sessions")
    except Exception as e:
        result.add_fail("GET /api/pro/sessions/{id} owner", str(e))
    
    # Test 18: GET /api/pro/sessions/{id} - different user gets 403
    print("\n" + "="*60)
    print("TEST 18: GET /api/pro/sessions/{id} (different user - expect 403)")
    print("="*60)
    try:
        # Get mei's session
        response = requests.get(f"{BASE_URL}/pro/sessions", headers=headers_mei, timeout=10)
        if response.status_code == 200:
            sessions = response.json()
            if len(sessions) > 0:
                session_id = sessions[0]["id"]
                # Try to access with diego's token
                response = requests.get(f"{BASE_URL}/pro/sessions/{session_id}", headers=headers_diego, timeout=10)
                if response.status_code == 403:
                    result.add_pass("GET /api/pro/sessions/{id} - different user gets 403")
                else:
                    result.add_fail("GET /api/pro/sessions/{id} 403", f"Expected 403, got {response.status_code}")
            else:
                result.add_fail("GET /api/pro/sessions/{id} 403", "No sessions to test")
        else:
            result.add_fail("GET /api/pro/sessions/{id} 403", "Failed to get sessions")
    except Exception as e:
        result.add_fail("GET /api/pro/sessions/{id} 403", str(e))
    
    # Test 19: GET /api/pro/sessions/{id} - nonexistent ID (should 404)
    print("\n" + "="*60)
    print("TEST 19: GET /api/pro/sessions/{id} (nonexistent - expect 404)")
    print("="*60)
    try:
        response = requests.get(f"{BASE_URL}/pro/sessions/nonexistent-id", headers=headers_mei, timeout=10)
        if response.status_code == 404:
            result.add_pass("GET /api/pro/sessions/{nonexistent} - returns 404")
        else:
            result.add_fail("GET /api/pro/sessions/{nonexistent}", f"Expected 404, got {response.status_code}")
    except Exception as e:
        result.add_fail("GET /api/pro/sessions/{nonexistent}", str(e))
    
    # Test 20: POST /api/pro/sessions/{id}/end - end session
    print("\n" + "="*60)
    print("TEST 20: POST /api/pro/sessions/{id}/end (end session)")
    print("="*60)
    try:
        # Get an active session
        response = requests.get(f"{BASE_URL}/pro/sessions", headers=headers_mei, timeout=10)
        if response.status_code == 200:
            sessions = response.json()
            active_session = next((s for s in sessions if s.get("status") == "active"), None)
            if active_session:
                session_id = active_session["id"]
                response = requests.post(f"{BASE_URL}/pro/sessions/{session_id}/end", headers=headers_mei, timeout=10)
                if response.status_code == 200:
                    session = response.json()
                    if (session.get("status") == "completed" and
                        session.get("end_time") and
                        session.get("call_duration") >= 0):
                        result.add_pass("POST /api/pro/sessions/{id}/end - sets completed status")
                    else:
                        result.add_fail("POST /api/pro/sessions/{id}/end", f"Invalid end state: {session}")
                else:
                    result.add_fail("POST /api/pro/sessions/{id}/end", f"Status {response.status_code}: {response.text}")
            else:
                result.add_fail("POST /api/pro/sessions/{id}/end", "No active sessions to end")
        else:
            result.add_fail("POST /api/pro/sessions/{id}/end", "Failed to get sessions")
    except Exception as e:
        result.add_fail("POST /api/pro/sessions/{id}/end", str(e))
    
    # Test 21: POST /api/pro/sessions/{id}/end - idempotent (call again)
    print("\n" + "="*60)
    print("TEST 21: POST /api/pro/sessions/{id}/end (idempotent)")
    print("="*60)
    try:
        # Get a completed session
        response = requests.get(f"{BASE_URL}/pro/sessions", headers=headers_mei, timeout=10)
        if response.status_code == 200:
            sessions = response.json()
            completed_session = next((s for s in sessions if s.get("status") == "completed"), None)
            if completed_session:
                session_id = completed_session["id"]
                response = requests.post(f"{BASE_URL}/pro/sessions/{session_id}/end", headers=headers_mei, timeout=10)
                if response.status_code == 200:
                    session = response.json()
                    if session.get("status") == "completed":
                        result.add_pass("POST /api/pro/sessions/{id}/end - idempotent (no error)")
                    else:
                        result.add_fail("POST /api/pro/sessions/{id}/end idempotent", f"Status changed: {session.get('status')}")
                else:
                    result.add_fail("POST /api/pro/sessions/{id}/end idempotent", f"Status {response.status_code}: {response.text}")
            else:
                result.add_fail("POST /api/pro/sessions/{id}/end idempotent", "No completed sessions to test")
        else:
            result.add_fail("POST /api/pro/sessions/{id}/end idempotent", "Failed to get sessions")
    except Exception as e:
        result.add_fail("POST /api/pro/sessions/{id}/end idempotent", str(e))
    
    # Test 22: GET /api/pro/wallet
    print("\n" + "="*60)
    print("TEST 22: GET /api/pro/wallet")
    print("="*60)
    try:
        response = requests.get(f"{BASE_URL}/pro/wallet", headers=headers_mei, timeout=10)
        if response.status_code == 200:
            wallet = response.json()
            if "balance" in wallet and "currency" in wallet:
                result.add_pass(f"GET /api/pro/wallet - returns balance={wallet['balance']}, currency={wallet['currency']}")
            else:
                result.add_fail("GET /api/pro/wallet", f"Missing fields: {wallet}")
        else:
            result.add_fail("GET /api/pro/wallet", f"Status {response.status_code}: {response.text}")
    except Exception as e:
        result.add_fail("GET /api/pro/wallet", str(e))
    
    # Test 23: GET /api/pro/progress
    print("\n" + "="*60)
    print("TEST 23: GET /api/pro/progress")
    print("="*60)
    try:
        response = requests.get(f"{BASE_URL}/pro/progress", headers=headers_mei, timeout=10)
        if response.status_code == 200:
            progress = response.json()
            required_fields = ["lessons_completed", "minutes_practiced", "tutors_met", "day_streak", "words_learned"]
            if all(field in progress for field in required_fields):
                if progress["lessons_completed"] >= 1:
                    result.add_pass(f"GET /api/pro/progress - returns all fields, lessons_completed={progress['lessons_completed']}")
                else:
                    result.add_fail("GET /api/pro/progress", f"Expected lessons_completed >= 1, got {progress['lessons_completed']}")
            else:
                result.add_fail("GET /api/pro/progress", f"Missing fields: {progress}")
        else:
            result.add_fail("GET /api/pro/progress", f"Status {response.status_code}: {response.text}")
    except Exception as e:
        result.add_fail("GET /api/pro/progress", str(e))
    
    # Test 24: GET /api/pro/availability - default empty
    print("\n" + "="*60)
    print("TEST 24: GET /api/pro/availability (default empty)")
    print("="*60)
    try:
        response = requests.get(f"{BASE_URL}/pro/availability", headers=headers_mei, timeout=10)
        if response.status_code == 200:
            data = response.json()
            if "blocks" in data and data["blocks"] == []:
                result.add_pass("GET /api/pro/availability - returns empty blocks by default")
            else:
                result.add_fail("GET /api/pro/availability default", f"Expected empty blocks, got {data}")
        else:
            result.add_fail("GET /api/pro/availability default", f"Status {response.status_code}: {response.text}")
    except Exception as e:
        result.add_fail("GET /api/pro/availability default", str(e))
    
    # Test 25: PUT /api/pro/availability - set blocks
    print("\n" + "="*60)
    print("TEST 25: PUT /api/pro/availability (set blocks)")
    print("="*60)
    try:
        blocks = [{"day": 0, "slot": "08:00"}, {"day": 1, "slot": "14:00"}]
        response = requests.put(f"{BASE_URL}/pro/availability", headers=headers_mei, json={"blocks": blocks}, timeout=10)
        if response.status_code == 200:
            data = response.json()
            if data.get("blocks") == blocks:
                result.add_pass("PUT /api/pro/availability - sets blocks")
            else:
                result.add_fail("PUT /api/pro/availability", f"Blocks not set correctly: {data}")
        else:
            result.add_fail("PUT /api/pro/availability", f"Status {response.status_code}: {response.text}")
    except Exception as e:
        result.add_fail("PUT /api/pro/availability", str(e))
    
    # Test 26: GET /api/pro/availability - verify blocks persisted
    print("\n" + "="*60)
    print("TEST 26: GET /api/pro/availability (verify persistence)")
    print("="*60)
    try:
        response = requests.get(f"{BASE_URL}/pro/availability", headers=headers_mei, timeout=10)
        if response.status_code == 200:
            data = response.json()
            blocks = data.get("blocks", [])
            if len(blocks) == 2 and blocks[0].get("day") == 0 and blocks[0].get("slot") == "08:00":
                result.add_pass("GET /api/pro/availability - blocks persisted correctly")
            else:
                result.add_fail("GET /api/pro/availability persistence", f"Blocks not persisted: {blocks}")
        else:
            result.add_fail("GET /api/pro/availability persistence", f"Status {response.status_code}: {response.text}")
    except Exception as e:
        result.add_fail("GET /api/pro/availability persistence", str(e))
    
    # Test 27: GET /api/pro/me without token (should 401/403)
    print("\n" + "="*60)
    print("TEST 27: GET /api/pro/me (no auth - expect 401/403)")
    print("="*60)
    try:
        response = requests.get(f"{BASE_URL}/pro/me", timeout=10)
        if response.status_code in [401, 403]:
            result.add_pass("GET /api/pro/me without auth - returns 401/403")
        else:
            result.add_fail("GET /api/pro/me no auth", f"Expected 401/403, got {response.status_code}")
    except Exception as e:
        result.add_fail("GET /api/pro/me no auth", str(e))
    
    # Test 28: GET /api/pro/wallet without token (should 401/403)
    print("\n" + "="*60)
    print("TEST 28: GET /api/pro/wallet (no auth - expect 401/403)")
    print("="*60)
    try:
        response = requests.get(f"{BASE_URL}/pro/wallet", timeout=10)
        if response.status_code in [401, 403]:
            result.add_pass("GET /api/pro/wallet without auth - returns 401/403")
        else:
            result.add_fail("GET /api/pro/wallet no auth", f"Expected 401/403, got {response.status_code}")
    except Exception as e:
        result.add_fail("GET /api/pro/wallet no auth", str(e))
    
    return result


if __name__ == "__main__":
    print("\n" + "="*60)
    print("PRO SUB-APP BACKEND API TEST SUITE")
    print("="*60)
    result = test_pro_endpoints()
    success = result.summary()
    exit(0 if success else 1)
