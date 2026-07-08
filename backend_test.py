"""
Backend testing for Learn module - Round 19
Tests all /api/learn/* endpoints with comprehensive coverage
"""

import requests
import json
from typing import Optional

# Backend URL from frontend/.env
BASE_URL = "https://voice-room-ui.preview.emergentagent.com/api"

# Test credentials
MEI_EMAIL = "mei@demo.com"
MEI_PASSWORD = "Demo1234!"
DIEGO_EMAIL = "diego@demo.com"
DIEGO_PASSWORD = "Demo1234!"

class TestResult:
    def __init__(self):
        self.passed = []
        self.failed = []
        self.warnings = []
    
    def add_pass(self, test_name: str, details: str = ""):
        self.passed.append(f"✅ {test_name}: {details}")
    
    def add_fail(self, test_name: str, details: str):
        self.failed.append(f"❌ {test_name}: {details}")
    
    def add_warning(self, test_name: str, details: str):
        self.warnings.append(f"⚠️  {test_name}: {details}")
    
    def print_summary(self):
        print("\n" + "="*80)
        print("LEARN MODULE BACKEND TEST RESULTS")
        print("="*80)
        
        if self.passed:
            print(f"\n✅ PASSED ({len(self.passed)}):")
            for p in self.passed:
                print(f"  {p}")
        
        if self.failed:
            print(f"\n❌ FAILED ({len(self.failed)}):")
            for f in self.failed:
                print(f"  {f}")
        
        if self.warnings:
            print(f"\n⚠️  WARNINGS ({len(self.warnings)}):")
            for w in self.warnings:
                print(f"  {w}")
        
        print(f"\n{'='*80}")
        print(f"TOTAL: {len(self.passed)} passed, {len(self.failed)} failed, {len(self.warnings)} warnings")
        print("="*80 + "\n")

result = TestResult()

def login(email: str, password: str) -> Optional[str]:
    """Login and return JWT token"""
    try:
        resp = requests.post(
            f"{BASE_URL}/auth/login",
            json={"email": email, "password": password},
            timeout=10
        )
        if resp.status_code == 200:
            return resp.json().get("token")
        else:
            print(f"Login failed for {email}: {resp.status_code} - {resp.text}")
            return None
    except Exception as e:
        print(f"Login exception for {email}: {e}")
        return None

def test_status_endpoint(token: str):
    """Test A: GET /api/learn/status"""
    print("\n[TEST A] Status endpoint")
    
    # A1: Basic status call
    try:
        resp = requests.get(
            f"{BASE_URL}/learn/status",
            headers={"Authorization": f"Bearer {token}"},
            timeout=10
        )
        
        if resp.status_code == 200:
            data = resp.json()
            required_keys = ["language", "due_count", "mistakes_count", "mastered_count", "total_vocab", "streak_days"]
            missing_keys = [k for k in required_keys if k not in data]
            
            if missing_keys:
                result.add_fail("A1: Status keys", f"Missing keys: {missing_keys}")
            else:
                # Verify types
                type_checks = [
                    (isinstance(data["language"], str), "language should be str"),
                    (isinstance(data["due_count"], int), "due_count should be int"),
                    (isinstance(data["mistakes_count"], int), "mistakes_count should be int"),
                    (isinstance(data["mastered_count"], int), "mastered_count should be int"),
                    (isinstance(data["total_vocab"], int), "total_vocab should be int"),
                    (isinstance(data["streak_days"], int), "streak_days should be int"),
                ]
                
                type_errors = [msg for check, msg in type_checks if not check]
                if type_errors:
                    result.add_fail("A1: Status types", f"Type errors: {type_errors}")
                else:
                    result.add_pass("A1: Status basic", f"All keys present with correct types. language={data['language']}, total_vocab={data['total_vocab']}")
        else:
            result.add_fail("A1: Status basic", f"Expected 200, got {resp.status_code}: {resp.text}")
    except Exception as e:
        result.add_fail("A1: Status basic", f"Exception: {e}")
    
    # A2: Status with language=es
    try:
        resp = requests.get(
            f"{BASE_URL}/learn/status?language=es",
            headers={"Authorization": f"Bearer {token}"},
            timeout=10
        )
        
        if resp.status_code == 200:
            data = resp.json()
            if data.get("language") == "es":
                if data.get("total_vocab", 0) >= 8:
                    result.add_pass("A2: Status language=es", f"language='es', total_vocab={data['total_vocab']} (>= 8)")
                else:
                    result.add_fail("A2: Status language=es", f"total_vocab={data['total_vocab']}, expected >= 8")
            else:
                result.add_fail("A2: Status language=es", f"language={data.get('language')}, expected 'es'")
        else:
            result.add_fail("A2: Status language=es", f"Expected 200, got {resp.status_code}: {resp.text}")
    except Exception as e:
        result.add_fail("A2: Status language=es", f"Exception: {e}")

def test_session_endpoint(token: str) -> Optional[str]:
    """Test B: GET /api/learn/session - returns first vocab_id for later tests"""
    print("\n[TEST B] Session endpoint")
    
    first_vocab_id = None
    
    try:
        resp = requests.get(
            f"{BASE_URL}/learn/session?language=en",
            headers={"Authorization": f"Bearer {token}"},
            timeout=10
        )
        
        if resp.status_code == 200:
            data = resp.json()
            
            # B1: Check response structure
            if "language" not in data or "cards" not in data:
                result.add_fail("B1: Session structure", f"Missing 'language' or 'cards' key")
                return None
            
            if data["language"] != "en":
                result.add_fail("B1: Session language", f"Expected language='en', got '{data['language']}'")
                return None
            
            cards = data["cards"]
            if not isinstance(cards, list):
                result.add_fail("B1: Session cards type", f"cards should be list, got {type(cards)}")
                return None
            
            # B2: Check cards length
            if len(cards) > 20:
                result.add_fail("B2: Session cards length", f"cards length {len(cards)} > 20")
            else:
                result.add_pass("B2: Session cards length", f"cards length={len(cards)} (<= 20)")
            
            # B3: Check card structure
            if len(cards) > 0:
                card = cards[0]
                required_card_keys = ["vocab_id", "word", "meaning", "language", "level", "is_new", "streak"]
                missing_card_keys = [k for k in required_card_keys if k not in card]
                
                if missing_card_keys:
                    result.add_fail("B3: Card structure", f"Missing keys in card: {missing_card_keys}")
                else:
                    # Check types
                    type_checks = [
                        (isinstance(card["vocab_id"], str), "vocab_id should be str"),
                        (isinstance(card["word"], str), "word should be str"),
                        (isinstance(card["meaning"], str), "meaning should be str"),
                        (card["language"] == "en", "language should be 'en'"),
                        (isinstance(card["is_new"], bool), "is_new should be bool"),
                        (isinstance(card["streak"], int), "streak should be int"),
                    ]
                    
                    type_errors = [msg for check, msg in type_checks if not check]
                    if type_errors:
                        result.add_fail("B3: Card types", f"Type errors: {type_errors}")
                    else:
                        first_vocab_id = card["vocab_id"]
                        result.add_pass("B3: Card structure", f"All card keys present with correct types. word='{card['word']}', is_new={card['is_new']}")
                        
                        # B4: Check is_new status (informational)
                        new_count = sum(1 for c in cards if c.get("is_new"))
                        result.add_pass("B4: Card is_new status", f"{new_count}/{len(cards)} cards are new")
            else:
                result.add_warning("B3: Card structure", "No cards returned, cannot verify card structure")
            
            return first_vocab_id
        else:
            result.add_fail("B1: Session request", f"Expected 200, got {resp.status_code}: {resp.text}")
            return None
    except Exception as e:
        result.add_fail("B1: Session request", f"Exception: {e}")
        return None

def test_review_endpoint(token: str, vocab_id: str):
    """Test C: POST /api/learn/review"""
    print("\n[TEST C] Review endpoint")
    
    if not vocab_id:
        result.add_fail("C: Review tests", "No vocab_id available from session")
        return
    
    # C1: Review with grade="correct"
    try:
        resp = requests.post(
            f"{BASE_URL}/learn/review",
            headers={"Authorization": f"Bearer {token}"},
            json={"vocab_id": vocab_id, "grade": "correct"},
            timeout=10
        )
        
        if resp.status_code == 200:
            data = resp.json()
            
            # Check response fields
            if data.get("streak") == 1 and data.get("interval_days", 0) >= 1 and data.get("last_result") == "correct":
                next_review = data.get("next_review")
                if next_review and isinstance(next_review, str):
                    result.add_pass("C1: Review correct", f"streak=1, interval_days={data['interval_days']}, next_review={next_review[:19]}, last_result='correct'")
                else:
                    result.add_fail("C1: Review correct", f"next_review is missing or invalid: {next_review}")
            else:
                result.add_fail("C1: Review correct", f"Unexpected values: streak={data.get('streak')}, interval_days={data.get('interval_days')}, last_result={data.get('last_result')}")
        else:
            result.add_fail("C1: Review correct", f"Expected 200, got {resp.status_code}: {resp.text}")
    except Exception as e:
        result.add_fail("C1: Review correct", f"Exception: {e}")
    
    # C2: Review with grade="wrong"
    try:
        resp = requests.post(
            f"{BASE_URL}/learn/review",
            headers={"Authorization": f"Bearer {token}"},
            json={"vocab_id": vocab_id, "grade": "wrong"},
            timeout=10
        )
        
        if resp.status_code == 200:
            data = resp.json()
            
            if data.get("streak") == 0 and data.get("interval_days") == 0 and data.get("last_result") == "wrong":
                result.add_pass("C2: Review wrong", f"streak=0, interval_days=0, last_result='wrong'")
            else:
                result.add_fail("C2: Review wrong", f"Unexpected values: streak={data.get('streak')}, interval_days={data.get('interval_days')}, last_result={data.get('last_result')}")
        else:
            result.add_fail("C2: Review wrong", f"Expected 200, got {resp.status_code}: {resp.text}")
    except Exception as e:
        result.add_fail("C2: Review wrong", f"Exception: {e}")
    
    # C3: Review with grade="hard"
    try:
        resp = requests.post(
            f"{BASE_URL}/learn/review",
            headers={"Authorization": f"Bearer {token}"},
            json={"vocab_id": vocab_id, "grade": "hard"},
            timeout=10
        )
        
        if resp.status_code == 200:
            data = resp.json()
            
            if data.get("last_result") == "hard" and data.get("streak") == 0:
                result.add_pass("C3: Review hard", f"last_result='hard', streak=0 (grade!=correct resets streak)")
            else:
                result.add_fail("C3: Review hard", f"Unexpected values: last_result={data.get('last_result')}, streak={data.get('streak')}")
        else:
            result.add_fail("C3: Review hard", f"Expected 200, got {resp.status_code}: {resp.text}")
    except Exception as e:
        result.add_fail("C3: Review hard", f"Exception: {e}")
    
    # C4: Review with grade="correct" again
    try:
        resp = requests.post(
            f"{BASE_URL}/learn/review",
            headers={"Authorization": f"Bearer {token}"},
            json={"vocab_id": vocab_id, "grade": "correct"},
            timeout=10
        )
        
        if resp.status_code == 200:
            data = resp.json()
            
            if data.get("streak") == 1:
                result.add_pass("C4: Review correct again", f"streak=1 (reset from previous correct)")
            else:
                result.add_fail("C4: Review correct again", f"Expected streak=1, got {data.get('streak')}")
        else:
            result.add_fail("C4: Review correct again", f"Expected 200, got {resp.status_code}: {resp.text}")
    except Exception as e:
        result.add_fail("C4: Review correct again", f"Exception: {e}")

def test_review_edge_cases(token: str):
    """Test D: Review edge cases"""
    print("\n[TEST D] Review edge cases")
    
    # D1: Unknown vocab_id
    try:
        resp = requests.post(
            f"{BASE_URL}/learn/review",
            headers={"Authorization": f"Bearer {token}"},
            json={"vocab_id": "nonexistent-id-xyz", "grade": "correct"},
            timeout=10
        )
        
        if resp.status_code == 404:
            detail = resp.json().get("detail", "")
            if "not found" in detail.lower():
                result.add_pass("D1: Unknown vocab_id", f"404 with message: '{detail}'")
            else:
                result.add_warning("D1: Unknown vocab_id", f"404 but unexpected message: '{detail}'")
        else:
            result.add_fail("D1: Unknown vocab_id", f"Expected 404, got {resp.status_code}: {resp.text}")
    except Exception as e:
        result.add_fail("D1: Unknown vocab_id", f"Exception: {e}")
    
    # D2: Invalid grade
    try:
        resp = requests.post(
            f"{BASE_URL}/learn/review",
            headers={"Authorization": f"Bearer {token}"},
            json={"vocab_id": "any-id", "grade": "maybe"},
            timeout=10
        )
        
        if resp.status_code == 422:
            result.add_pass("D2: Invalid grade", f"422 validation error for grade='maybe'")
        else:
            result.add_fail("D2: Invalid grade", f"Expected 422, got {resp.status_code}: {resp.text}")
    except Exception as e:
        result.add_fail("D2: Invalid grade", f"Exception: {e}")

def test_vocabulary_endpoint(token: str):
    """Test E: GET /api/learn/vocabulary"""
    print("\n[TEST E] Vocabulary list")
    
    try:
        resp = requests.get(
            f"{BASE_URL}/learn/vocabulary?language=en",
            headers={"Authorization": f"Bearer {token}"},
            timeout=10
        )
        
        if resp.status_code == 200:
            data = resp.json()
            
            if not isinstance(data, list):
                result.add_fail("E1: Vocabulary type", f"Expected list, got {type(data)}")
                return
            
            if len(data) == 0:
                result.add_warning("E1: Vocabulary list", "Empty vocabulary list")
                return
            
            # Check structure of first item
            item = data[0]
            required_keys = ["id", "word", "meaning", "language", "level", "seen", "streak", "last_result"]
            missing_keys = [k for k in required_keys if k not in item]
            
            if missing_keys:
                result.add_fail("E1: Vocabulary structure", f"Missing keys: {missing_keys}")
            else:
                # Check types
                type_checks = [
                    (isinstance(item["id"], str), "id should be str"),
                    (isinstance(item["word"], str), "word should be str"),
                    (isinstance(item["meaning"], str), "meaning should be str"),
                    (item["language"] == "en", "language should be 'en'"),
                    (isinstance(item["seen"], bool), "seen should be bool"),
                    (isinstance(item["streak"], int), "streak should be int"),
                ]
                
                type_errors = [msg for check, msg in type_checks if not check]
                if type_errors:
                    result.add_fail("E1: Vocabulary types", f"Type errors: {type_errors}")
                else:
                    result.add_pass("E1: Vocabulary structure", f"All keys present with correct types. Total items: {len(data)}")
            
            # E2: Check if any item has seen=true (after previous reviews)
            seen_items = [i for i in data if i.get("seen")]
            if seen_items:
                result.add_pass("E2: Vocabulary seen status", f"{len(seen_items)}/{len(data)} items have seen=true")
            else:
                result.add_warning("E2: Vocabulary seen status", "No items with seen=true (expected at least one after reviews)")
        else:
            result.add_fail("E1: Vocabulary request", f"Expected 200, got {resp.status_code}: {resp.text}")
    except Exception as e:
        result.add_fail("E1: Vocabulary request", f"Exception: {e}")

def test_mistakes_endpoint(token: str):
    """Test F: GET /api/learn/mistakes"""
    print("\n[TEST F] Mistakes endpoint")
    
    try:
        resp = requests.get(
            f"{BASE_URL}/learn/mistakes",
            headers={"Authorization": f"Bearer {token}"},
            timeout=10
        )
        
        if resp.status_code == 200:
            data = resp.json()
            
            if not isinstance(data, list):
                result.add_fail("F1: Mistakes type", f"Expected list, got {type(data)}")
                return
            
            # After marking a word wrong in test C2, we should have at least one mistake
            if len(data) > 0:
                result.add_pass("F1: Mistakes list", f"Found {len(data)} mistake(s) after marking word wrong")
                
                # Check structure
                item = data[0]
                if "vocab_id" in item and "word" in item and "meaning" in item:
                    result.add_pass("F2: Mistakes structure", f"Mistake item has required fields: word='{item.get('word')}'")
                else:
                    result.add_fail("F2: Mistakes structure", f"Missing required fields in mistake item")
            else:
                result.add_warning("F1: Mistakes list", "No mistakes found (expected at least one after test C2)")
        else:
            result.add_fail("F1: Mistakes request", f"Expected 200, got {resp.status_code}: {resp.text}")
    except Exception as e:
        result.add_fail("F1: Mistakes request", f"Exception: {e}")

def test_collections_endpoint(token: str):
    """Test G: Collections endpoints"""
    print("\n[TEST G] Collections endpoints")
    
    # G1: Create collection
    collection_id = None
    try:
        resp = requests.post(
            f"{BASE_URL}/learn/collections",
            headers={"Authorization": f"Bearer {token}"},
            json={"name": "My Favorite Words", "language": "en", "vocab_ids": ["x", "y", "z"]},
            timeout=10
        )
        
        if resp.status_code == 201:
            data = resp.json()
            
            required_keys = ["id", "name", "language", "count", "created_at"]
            missing_keys = [k for k in required_keys if k not in data]
            
            if missing_keys:
                result.add_fail("G1: Create collection", f"Missing keys: {missing_keys}")
            else:
                if data["name"] == "My Favorite Words" and data["language"] == "en" and data["count"] == 3:
                    collection_id = data["id"]
                    result.add_pass("G1: Create collection", f"Created collection: name='{data['name']}', language='en', count=3, id={collection_id}")
                else:
                    result.add_fail("G1: Create collection", f"Unexpected values: name={data['name']}, language={data['language']}, count={data['count']}")
        else:
            result.add_fail("G1: Create collection", f"Expected 201, got {resp.status_code}: {resp.text}")
    except Exception as e:
        result.add_fail("G1: Create collection", f"Exception: {e}")
    
    # G2: List collections
    try:
        resp = requests.get(
            f"{BASE_URL}/learn/collections",
            headers={"Authorization": f"Bearer {token}"},
            timeout=10
        )
        
        if resp.status_code == 200:
            data = resp.json()
            
            if not isinstance(data, list):
                result.add_fail("G2: List collections type", f"Expected list, got {type(data)}")
            else:
                # Find our created collection
                found = any(c.get("name") == "My Favorite Words" and c.get("count") == 3 for c in data)
                if found:
                    result.add_pass("G2: List collections", f"Found 'My Favorite Words' collection in list (total: {len(data)} collections)")
                else:
                    result.add_fail("G2: List collections", f"'My Favorite Words' collection not found in list")
        else:
            result.add_fail("G2: List collections", f"Expected 200, got {resp.status_code}: {resp.text}")
    except Exception as e:
        result.add_fail("G2: List collections", f"Exception: {e}")
    
    # G3: Create collection with empty name (should fail)
    try:
        resp = requests.post(
            f"{BASE_URL}/learn/collections",
            headers={"Authorization": f"Bearer {token}"},
            json={"name": "", "language": "en", "vocab_ids": []},
            timeout=10
        )
        
        if resp.status_code == 422:
            result.add_pass("G3: Empty name validation", "422 validation error for empty name")
        else:
            result.add_fail("G3: Empty name validation", f"Expected 422, got {resp.status_code}: {resp.text}")
    except Exception as e:
        result.add_fail("G3: Empty name validation", f"Exception: {e}")

def test_auth_required():
    """Test H: Auth required on all endpoints"""
    print("\n[TEST H] Auth required")
    
    endpoints = [
        ("GET", "/learn/status"),
        ("GET", "/learn/session"),
        ("POST", "/learn/review", {"vocab_id": "test", "grade": "correct"}),
        ("GET", "/learn/vocabulary"),
        ("GET", "/learn/mistakes"),
        ("GET", "/learn/collections"),
        ("POST", "/learn/collections", {"name": "Test"}),
    ]
    
    failed_auth = []
    for method, path, *body in endpoints:
        try:
            if method == "GET":
                resp = requests.get(f"{BASE_URL}{path}", timeout=10)
            else:
                resp = requests.post(f"{BASE_URL}{path}", json=body[0] if body else {}, timeout=10)
            
            if resp.status_code not in [401, 403]:
                failed_auth.append(f"{method} {path} returned {resp.status_code} (expected 401/403)")
        except Exception as e:
            failed_auth.append(f"{method} {path} exception: {e}")
    
    if failed_auth:
        result.add_fail("H: Auth required", f"Some endpoints don't require auth: {failed_auth}")
    else:
        result.add_pass("H: Auth required", f"All {len(endpoints)} endpoints correctly require authentication (401/403)")

def main():
    print("="*80)
    print("LEARN MODULE BACKEND TESTING - ROUND 19")
    print("="*80)
    print(f"Backend URL: {BASE_URL}")
    print(f"Test user: {MEI_EMAIL}")
    
    # Login
    print("\n[SETUP] Logging in as mei@demo.com...")
    mei_token = login(MEI_EMAIL, MEI_PASSWORD)
    
    if not mei_token:
        print("❌ CRITICAL: Failed to login as mei@demo.com")
        result.add_fail("Setup", "Failed to login as mei@demo.com")
        result.print_summary()
        return
    
    print("✅ Login successful")
    
    # Run all tests
    test_status_endpoint(mei_token)
    first_vocab_id = test_session_endpoint(mei_token)
    test_review_endpoint(mei_token, first_vocab_id)
    test_review_edge_cases(mei_token)
    test_vocabulary_endpoint(mei_token)
    test_mistakes_endpoint(mei_token)
    test_collections_endpoint(mei_token)
    test_auth_required()
    
    # Print summary
    result.print_summary()

if __name__ == "__main__":
    main()
