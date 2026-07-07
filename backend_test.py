#!/usr/bin/env python3
"""
Round 17b — Backend Test: GET /api/moments/{id} returns poll field correctly
Bug fix verification for poll field in single moment endpoint.
"""

import requests
import sys
from typing import Optional

# Backend URL from frontend/.env
BASE_URL = "https://23e89f0c-4dcc-40fe-82d2-2e242a0a0207.preview.emergentagent.com/api"

# Test credentials
MEI_EMAIL = "mei@demo.com"
MEI_PASSWORD = "Demo1234!"

class TestRunner:
    def __init__(self):
        self.mei_token: Optional[str] = None
        self.passed = 0
        self.failed = 0
        self.test_moments = []  # Track created moments for cleanup context
        
    def log(self, message: str, level: str = "INFO"):
        """Log test messages"""
        prefix = {
            "INFO": "ℹ️",
            "PASS": "✅",
            "FAIL": "❌",
            "STEP": "🔹"
        }.get(level, "•")
        print(f"{prefix} {message}")
        
    def login_mei(self) -> bool:
        """Login as mei@demo.com"""
        self.log("Logging in as mei@demo.com...", "STEP")
        try:
            response = requests.post(
                f"{BASE_URL}/auth/login",
                json={"email": MEI_EMAIL, "password": MEI_PASSWORD},
                timeout=10
            )
            if response.status_code == 200:
                data = response.json()
                self.mei_token = data.get("token")
                self.log(f"Login successful. Token: {self.mei_token[:20]}...", "PASS")
                return True
            else:
                self.log(f"Login failed: {response.status_code} - {response.text}", "FAIL")
                return False
        except Exception as e:
            self.log(f"Login exception: {e}", "FAIL")
            return False
            
    def test_a_create_moment_with_poll(self) -> Optional[str]:
        """A) Create moment with poll"""
        self.log("\n=== TEST A: Create moment with poll ===", "INFO")
        
        try:
            response = requests.post(
                f"{BASE_URL}/moments",
                headers={"Authorization": f"Bearer {self.mei_token}"},
                json={
                    "text": "Pizza or Burger?",
                    "poll": {
                        "options": [
                            {"text": "Pizza"},
                            {"text": "Burger"}
                        ]
                    }
                },
                timeout=10
            )
            
            if response.status_code == 201:
                data = response.json()
                moment_id = data.get("id")
                self.test_moments.append(moment_id)
                self.log(f"POST /api/moments → 201 ✓", "PASS")
                self.log(f"Moment ID: {moment_id}", "INFO")
                self.passed += 1
                return moment_id
            else:
                self.log(f"POST /api/moments → {response.status_code} (expected 201)", "FAIL")
                self.log(f"Response: {response.text}", "FAIL")
                self.failed += 1
                return None
        except Exception as e:
            self.log(f"Exception creating moment: {e}", "FAIL")
            self.failed += 1
            return None
            
    def test_b_get_single_moment_returns_poll(self, moment_id: str) -> bool:
        """B) GET single moment returns poll"""
        self.log("\n=== TEST B: GET single moment returns poll ===", "INFO")
        
        try:
            response = requests.get(
                f"{BASE_URL}/moments/{moment_id}",
                headers={"Authorization": f"Bearer {self.mei_token}"},
                timeout=10
            )
            
            if response.status_code != 200:
                self.log(f"GET /api/moments/{moment_id} → {response.status_code} (expected 200)", "FAIL")
                self.failed += 1
                return False
                
            data = response.json()
            self.log(f"GET /api/moments/{moment_id} → 200 ✓", "PASS")
            
            # Verify poll field is not null
            if data.get("poll") is None:
                self.log("FAIL: response.poll is null (expected poll object)", "FAIL")
                self.failed += 1
                return False
            
            poll = data["poll"]
            self.log(f"Poll field present: {poll}", "PASS")
            
            # Verify poll structure
            checks = []
            
            # Check question (null or string)
            question = poll.get("question")
            if question is None or isinstance(question, str):
                checks.append(("question", True, f"question={question}"))
            else:
                checks.append(("question", False, f"question type is {type(question)}, expected null or string"))
            
            # Check options (array of exactly 2 items)
            options = poll.get("options")
            if not isinstance(options, list):
                checks.append(("options", False, f"options is not a list: {type(options)}"))
            elif len(options) != 2:
                checks.append(("options", False, f"options has {len(options)} items, expected 2"))
            else:
                checks.append(("options", True, f"options has 2 items"))
                
                # Check each option has text + votes
                for i, opt in enumerate(options):
                    if "text" not in opt:
                        checks.append((f"options[{i}].text", False, "missing text field"))
                    elif not isinstance(opt["text"], str):
                        checks.append((f"options[{i}].text", False, f"text is {type(opt['text'])}, expected string"))
                    else:
                        checks.append((f"options[{i}].text", True, f"text='{opt['text']}'"))
                    
                    if "votes" not in opt:
                        checks.append((f"options[{i}].votes", False, "missing votes field"))
                    elif not isinstance(opt["votes"], int):
                        checks.append((f"options[{i}].votes", False, f"votes is {type(opt['votes'])}, expected int"))
                    else:
                        checks.append((f"options[{i}].votes", True, f"votes={opt['votes']}"))
            
            # Check total_votes == 0
            total_votes = poll.get("total_votes")
            if total_votes == 0:
                checks.append(("total_votes", True, "total_votes=0"))
            else:
                checks.append(("total_votes", False, f"total_votes={total_votes}, expected 0"))
            
            # Check my_vote == null
            my_vote = poll.get("my_vote")
            if my_vote is None:
                checks.append(("my_vote", True, "my_vote=null"))
            else:
                checks.append(("my_vote", False, f"my_vote={my_vote}, expected null"))
            
            # Check tags field is present
            if "tags" in data:
                checks.append(("tags", True, f"tags={data['tags']}"))
            else:
                checks.append(("tags", False, "tags field missing"))
            
            # Check comments field is present
            if "comments" in data:
                checks.append(("comments", True, f"comments array present (length={len(data['comments'])})"))
            else:
                checks.append(("comments", False, "comments field missing"))
            
            # Report all checks
            all_passed = True
            for field, passed, msg in checks:
                if passed:
                    self.log(f"  ✓ {field}: {msg}", "PASS")
                else:
                    self.log(f"  ✗ {field}: {msg}", "FAIL")
                    all_passed = False
            
            if all_passed:
                self.passed += 1
                return True
            else:
                self.failed += 1
                return False
                
        except Exception as e:
            self.log(f"Exception getting moment: {e}", "FAIL")
            self.failed += 1
            return False
            
    def test_c_vote_then_get_again(self, moment_id: str) -> bool:
        """C) Vote then GET again"""
        self.log("\n=== TEST C: Vote then GET again ===", "INFO")
        
        try:
            # Step 1: Vote for option 1 (Burger)
            self.log("Step 1: POST /api/moments/{moment_id}/vote with option_index=1", "STEP")
            response = requests.post(
                f"{BASE_URL}/moments/{moment_id}/vote",
                headers={"Authorization": f"Bearer {self.mei_token}"},
                json={"option_index": 1},
                timeout=10
            )
            
            if response.status_code != 200:
                self.log(f"POST /api/moments/{moment_id}/vote → {response.status_code} (expected 200)", "FAIL")
                self.log(f"Response: {response.text}", "FAIL")
                self.failed += 1
                return False
            
            self.log(f"POST /api/moments/{moment_id}/vote → 200 ✓", "PASS")
            
            # Step 2: GET moment again
            self.log("Step 2: GET /api/moments/{moment_id} again", "STEP")
            response = requests.get(
                f"{BASE_URL}/moments/{moment_id}",
                headers={"Authorization": f"Bearer {self.mei_token}"},
                timeout=10
            )
            
            if response.status_code != 200:
                self.log(f"GET /api/moments/{moment_id} → {response.status_code} (expected 200)", "FAIL")
                self.failed += 1
                return False
            
            data = response.json()
            self.log(f"GET /api/moments/{moment_id} → 200 ✓", "PASS")
            
            poll = data.get("poll")
            if not poll:
                self.log("FAIL: poll field missing after vote", "FAIL")
                self.failed += 1
                return False
            
            # Verify vote results
            checks = []
            
            my_vote = poll.get("my_vote")
            if my_vote == 1:
                checks.append(("my_vote", True, "my_vote=1"))
            else:
                checks.append(("my_vote", False, f"my_vote={my_vote}, expected 1"))
            
            options = poll.get("options", [])
            if len(options) >= 2:
                if options[1].get("votes") == 1:
                    checks.append(("options[1].votes", True, "options[1].votes=1"))
                else:
                    checks.append(("options[1].votes", False, f"options[1].votes={options[1].get('votes')}, expected 1"))
                
                if options[0].get("votes") == 0:
                    checks.append(("options[0].votes", True, "options[0].votes=0"))
                else:
                    checks.append(("options[0].votes", False, f"options[0].votes={options[0].get('votes')}, expected 0"))
            else:
                checks.append(("options", False, f"options has {len(options)} items, expected 2"))
            
            total_votes = poll.get("total_votes")
            if total_votes == 1:
                checks.append(("total_votes", True, "total_votes=1"))
            else:
                checks.append(("total_votes", False, f"total_votes={total_votes}, expected 1"))
            
            # Report all checks
            all_passed = True
            for field, passed, msg in checks:
                if passed:
                    self.log(f"  ✓ {field}: {msg}", "PASS")
                else:
                    self.log(f"  ✗ {field}: {msg}", "FAIL")
                    all_passed = False
            
            if all_passed:
                self.passed += 1
                return True
            else:
                self.failed += 1
                return False
                
        except Exception as e:
            self.log(f"Exception in vote test: {e}", "FAIL")
            self.failed += 1
            return False
            
    def test_d_moment_without_poll(self) -> bool:
        """D) Regression — moment without poll"""
        self.log("\n=== TEST D: Regression — moment without poll ===", "INFO")
        
        try:
            # Step 1: Create moment with just text
            self.log("Step 1: POST /api/moments with just text", "STEP")
            response = requests.post(
                f"{BASE_URL}/moments",
                headers={"Authorization": f"Bearer {self.mei_token}"},
                json={"text": "just text"},
                timeout=10
            )
            
            if response.status_code != 201:
                self.log(f"POST /api/moments → {response.status_code} (expected 201)", "FAIL")
                self.log(f"Response: {response.text}", "FAIL")
                self.failed += 1
                return False
            
            data = response.json()
            plain_id = data.get("id")
            self.test_moments.append(plain_id)
            self.log(f"POST /api/moments → 201 ✓ (ID: {plain_id})", "PASS")
            
            # Step 2: GET the plain moment
            self.log("Step 2: GET /api/moments/{plain_id}", "STEP")
            response = requests.get(
                f"{BASE_URL}/moments/{plain_id}",
                headers={"Authorization": f"Bearer {self.mei_token}"},
                timeout=10
            )
            
            if response.status_code != 200:
                self.log(f"GET /api/moments/{plain_id} → {response.status_code} (expected 200)", "FAIL")
                self.failed += 1
                return False
            
            data = response.json()
            self.log(f"GET /api/moments/{plain_id} → 200 ✓", "PASS")
            
            # Verify poll is null or absent
            checks = []
            
            poll = data.get("poll")
            if poll is None or "poll" not in data:
                checks.append(("poll", True, "poll is null or absent"))
            else:
                checks.append(("poll", False, f"poll={poll}, expected null"))
            
            # Verify text
            text = data.get("text")
            if text == "just text":
                checks.append(("text", True, "text='just text'"))
            else:
                checks.append(("text", False, f"text='{text}', expected 'just text'"))
            
            # Verify response doesn't crash (has expected fields)
            if "id" in data and "author" in data:
                checks.append(("structure", True, "response has expected structure"))
            else:
                checks.append(("structure", False, "response missing expected fields"))
            
            # Report all checks
            all_passed = True
            for field, passed, msg in checks:
                if passed:
                    self.log(f"  ✓ {field}: {msg}", "PASS")
                else:
                    self.log(f"  ✗ {field}: {msg}", "FAIL")
                    all_passed = False
            
            if all_passed:
                self.passed += 1
                return True
            else:
                self.failed += 1
                return False
                
        except Exception as e:
            self.log(f"Exception in plain moment test: {e}", "FAIL")
            self.failed += 1
            return False
            
    def test_e_get_list_returns_poll(self) -> bool:
        """E) Regression — GET list still returns poll"""
        self.log("\n=== TEST E: Regression — GET list still returns poll ===", "INFO")
        
        try:
            response = requests.get(
                f"{BASE_URL}/moments",
                headers={"Authorization": f"Bearer {self.mei_token}"},
                timeout=10
            )
            
            if response.status_code != 200:
                self.log(f"GET /api/moments → {response.status_code} (expected 200)", "FAIL")
                self.failed += 1
                return False
            
            data = response.json()
            self.log(f"GET /api/moments → 200 ✓ (found {len(data)} moments)", "PASS")
            
            if not isinstance(data, list):
                self.log(f"FAIL: response is not a list: {type(data)}", "FAIL")
                self.failed += 1
                return False
            
            # Find our test moments in the list
            poll_moment = None
            plain_moment = None
            
            for moment in data:
                if moment.get("id") in self.test_moments:
                    if moment.get("text") == "Pizza or Burger?":
                        poll_moment = moment
                    elif moment.get("text") == "just text":
                        plain_moment = moment
            
            checks = []
            
            # Verify poll moment has poll
            if poll_moment:
                if poll_moment.get("poll") is not None:
                    poll_data = poll_moment["poll"]
                    if isinstance(poll_data.get("options"), list) and len(poll_data["options"]) == 2:
                        checks.append(("poll_moment", True, f"poll moment has poll with 2 options"))
                    else:
                        checks.append(("poll_moment", False, f"poll moment has invalid poll structure"))
                else:
                    checks.append(("poll_moment", False, "poll moment missing poll field"))
            else:
                checks.append(("poll_moment", False, "poll moment not found in list"))
            
            # Verify plain moment has null poll
            if plain_moment:
                if plain_moment.get("poll") is None or "poll" not in plain_moment:
                    checks.append(("plain_moment", True, "plain moment has null/absent poll"))
                else:
                    checks.append(("plain_moment", False, f"plain moment has poll={plain_moment.get('poll')}, expected null"))
            else:
                checks.append(("plain_moment", False, "plain moment not found in list"))
            
            # Report all checks
            all_passed = True
            for field, passed, msg in checks:
                if passed:
                    self.log(f"  ✓ {field}: {msg}", "PASS")
                else:
                    self.log(f"  ✗ {field}: {msg}", "FAIL")
                    all_passed = False
            
            if all_passed:
                self.passed += 1
                return True
            else:
                self.failed += 1
                return False
                
        except Exception as e:
            self.log(f"Exception in list test: {e}", "FAIL")
            self.failed += 1
            return False
            
    def test_f_poll_only_no_text(self) -> bool:
        """F) Regression — moment with only poll and no text"""
        self.log("\n=== TEST F: Regression — moment with only poll and no text ===", "INFO")
        
        try:
            # Step 1: Create moment with only poll (no text)
            self.log("Step 1: POST /api/moments with only poll (no text)", "STEP")
            response = requests.post(
                f"{BASE_URL}/moments",
                headers={"Authorization": f"Bearer {self.mei_token}"},
                json={
                    "poll": {
                        "options": [
                            {"text": "A"},
                            {"text": "B"}
                        ]
                    }
                },
                timeout=10
            )
            
            if response.status_code != 201:
                self.log(f"POST /api/moments → {response.status_code} (expected 201)", "FAIL")
                self.log(f"Response: {response.text}", "FAIL")
                self.failed += 1
                return False
            
            data = response.json()
            new_id = data.get("id")
            self.test_moments.append(new_id)
            self.log(f"POST /api/moments → 201 ✓ (ID: {new_id})", "PASS")
            
            # Step 2: GET the poll-only moment
            self.log("Step 2: GET /api/moments/{new_id}", "STEP")
            response = requests.get(
                f"{BASE_URL}/moments/{new_id}",
                headers={"Authorization": f"Bearer {self.mei_token}"},
                timeout=10
            )
            
            if response.status_code != 200:
                self.log(f"GET /api/moments/{new_id} → {response.status_code} (expected 200)", "FAIL")
                self.failed += 1
                return False
            
            data = response.json()
            self.log(f"GET /api/moments/{new_id} → 200 ✓", "PASS")
            
            # Verify poll present and text empty
            checks = []
            
            poll = data.get("poll")
            if poll is not None:
                if isinstance(poll.get("options"), list) and len(poll["options"]) == 2:
                    checks.append(("poll", True, "poll present with 2 options"))
                else:
                    checks.append(("poll", False, f"poll has invalid structure"))
            else:
                checks.append(("poll", False, "poll is null, expected poll object"))
            
            text = data.get("text")
            if text == "" or text is None:
                checks.append(("text", True, f"text is empty string or null"))
            else:
                checks.append(("text", False, f"text='{text}', expected empty string"))
            
            # Report all checks
            all_passed = True
            for field, passed, msg in checks:
                if passed:
                    self.log(f"  ✓ {field}: {msg}", "PASS")
                else:
                    self.log(f"  ✗ {field}: {msg}", "FAIL")
                    all_passed = False
            
            if all_passed:
                self.passed += 1
                return True
            else:
                self.failed += 1
                return False
                
        except Exception as e:
            self.log(f"Exception in poll-only test: {e}", "FAIL")
            self.failed += 1
            return False
            
    def run_all_tests(self):
        """Run all test scenarios"""
        self.log("=" * 80, "INFO")
        self.log("Round 17b — GET /api/moments/{id} Poll Field Bug Fix Verification", "INFO")
        self.log("=" * 80, "INFO")
        
        # Login
        if not self.login_mei():
            self.log("\n❌ Login failed. Cannot proceed with tests.", "FAIL")
            return False
        
        # Test A: Create moment with poll
        moment_id = self.test_a_create_moment_with_poll()
        if not moment_id:
            self.log("\n❌ Test A failed. Cannot proceed with dependent tests.", "FAIL")
            return False
        
        # Test B: GET single moment returns poll
        self.test_b_get_single_moment_returns_poll(moment_id)
        
        # Test C: Vote then GET again
        self.test_c_vote_then_get_again(moment_id)
        
        # Test D: Moment without poll
        self.test_d_moment_without_poll()
        
        # Test E: GET list returns poll
        self.test_e_get_list_returns_poll()
        
        # Test F: Poll-only moment (no text)
        self.test_f_poll_only_no_text()
        
        # Summary
        self.log("\n" + "=" * 80, "INFO")
        self.log("TEST SUMMARY", "INFO")
        self.log("=" * 80, "INFO")
        self.log(f"Total Passed: {self.passed}", "PASS" if self.passed > 0 else "INFO")
        self.log(f"Total Failed: {self.failed}", "FAIL" if self.failed > 0 else "INFO")
        
        if self.failed == 0:
            self.log("\n🎉 ALL TESTS PASSED!", "PASS")
            return True
        else:
            self.log(f"\n⚠️  {self.failed} TEST(S) FAILED", "FAIL")
            return False

def main():
    runner = TestRunner()
    success = runner.run_all_tests()
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()
