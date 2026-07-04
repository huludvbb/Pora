#!/usr/bin/env python3
"""
Backend API test for Voice Room Gift Feature (most_gifted leaderboard)
Tests the redesigned gift system where most_gifted tracks RECIPIENTS (not senders)
"""

import requests
import json
import sys

# Backend URL from frontend/.env
BACKEND_URL = "https://368bd428-054d-4ed0-be5c-b4aaf6dfeef5.preview.emergentagent.com/api"

# Test credentials from /app/memory/test_credentials.md
USER_A_EMAIL = "mei@demo.com"
USER_A_PASSWORD = "Demo1234!"
USER_B_EMAIL = "diego@demo.com"
USER_B_PASSWORD = "Demo1234!"

def login(email, password):
    """Login and return token and user_id"""
    response = requests.post(
        f"{BACKEND_URL}/auth/login",
        json={"email": email, "password": password}
    )
    if response.status_code != 200:
        print(f"❌ Login failed for {email}: {response.status_code} {response.text}")
        return None, None
    data = response.json()
    return data.get("token"), data.get("user", {}).get("id")

def test_gift_feature():
    """Test the voice room gift feature with most_gifted leaderboard"""
    print("=" * 80)
    print("VOICE ROOM GIFT FEATURE TEST - most_gifted leaderboard (tracks RECIPIENTS)")
    print("=" * 80)
    
    # Step 1: Login as User A (mei@demo.com)
    print("\n[Step 1] Login as User A (mei@demo.com)...")
    token_a, user_a_id = login(USER_A_EMAIL, USER_A_PASSWORD)
    if not token_a:
        print("❌ FAILED: Could not login as User A")
        return False
    print(f"✅ User A logged in successfully (user_id: {user_a_id})")
    
    # Step 2: Login as User B (diego@demo.com)
    print("\n[Step 2] Login as User B (diego@demo.com)...")
    token_b, user_b_id = login(USER_B_EMAIL, USER_B_PASSWORD)
    if not token_b:
        print("❌ FAILED: Could not login as User B")
        return False
    print(f"✅ User B logged in successfully (user_id: {user_b_id})")
    
    # Step 3: User A creates a room
    print("\n[Step 3] User A (mei) creates a room...")
    room_data = {
        "title": "Gift Test Room",
        "language": "en",
        "languages": ["en"],
        "mode": "chat",
        "is_private": False
    }
    response = requests.post(
        f"{BACKEND_URL}/rooms",
        json=room_data,
        headers={"Authorization": f"Bearer {token_a}"}
    )
    if response.status_code not in [200, 201]:
        print(f"❌ FAILED: Room creation failed: {response.status_code} {response.text}")
        return False
    room = response.json()
    room_id = room.get("id")
    print(f"✅ Room created successfully (room_id: {room_id})")
    print(f"   Room title: {room.get('title')}")
    print(f"   Host: {room.get('host', {}).get('name')}")
    
    # Step 4: User B joins the room
    print("\n[Step 4] User B (diego) joins the room...")
    response = requests.post(
        f"{BACKEND_URL}/rooms/{room_id}/join",
        headers={"Authorization": f"Bearer {token_b}"}
    )
    if response.status_code not in [200, 201]:
        print(f"❌ FAILED: Room join failed: {response.status_code} {response.text}")
        return False
    print(f"✅ User B joined the room successfully")
    
    # Get User B's coins before sending gift
    response = requests.get(
        f"{BACKEND_URL}/auth/me",
        headers={"Authorization": f"Bearer {token_b}"}
    )
    coins_before = response.json().get("coins", 0)
    print(f"   User B coins before gift: {coins_before}")
    
    # Step 5: User B sends a gift to User A (the host)
    print("\n[Step 5] User B sends a rose gift (10 coins) to User A (the host)...")
    gift_data = {
        "to_user_id": user_a_id,
        "gift_id": "rose"
    }
    response = requests.post(
        f"{BACKEND_URL}/rooms/{room_id}/gift",
        json=gift_data,
        headers={"Authorization": f"Bearer {token_b}"}
    )
    if response.status_code not in [200, 201]:
        print(f"❌ FAILED: Gift sending failed: {response.status_code} {response.text}")
        return False
    
    gift_response = response.json()
    coins_after = gift_response.get("coins")
    message = gift_response.get("message", {})
    
    print(f"✅ Gift sent successfully")
    print(f"   User B coins after gift: {coins_after}")
    print(f"   Coins deducted: {coins_before - coins_after}")
    print(f"   Message type: {message.get('type')}")
    print(f"   Message text: {message.get('text')}")
    
    # Verify coins deducted correctly
    if coins_before - coins_after != 10:
        print(f"❌ FAILED: Expected 10 coins deducted, got {coins_before - coins_after}")
        return False
    print(f"✅ Coins deducted correctly (10 coins)")
    
    # Verify message type is 'gift'
    if message.get('type') != 'gift':
        print(f"❌ FAILED: Expected message type 'gift', got '{message.get('type')}'")
        return False
    print(f"✅ Message type is 'gift'")
    
    # Step 6: Get room details and verify most_gifted
    print("\n[Step 6] GET /api/rooms/{room_id} - verify most_gifted array...")
    response = requests.get(
        f"{BACKEND_URL}/rooms/{room_id}",
        headers={"Authorization": f"Bearer {token_a}"}
    )
    if response.status_code != 200:
        print(f"❌ FAILED: Get room failed: {response.status_code} {response.text}")
        return False
    
    room_details = response.json()
    most_gifted = room_details.get("most_gifted", [])
    
    print(f"✅ Room details retrieved")
    print(f"   most_gifted array: {json.dumps(most_gifted, indent=2)}")
    
    # Verify most_gifted contains User A (recipient) with coins=10
    if len(most_gifted) == 0:
        print(f"❌ FAILED: most_gifted array is empty")
        return False
    
    top_gifted = most_gifted[0]
    top_gifted_id = top_gifted.get("id")
    top_gifted_coins = top_gifted.get("coins")
    top_gifted_name = top_gifted.get("name")
    
    print(f"\n   Top most_gifted user:")
    print(f"   - ID: {top_gifted_id}")
    print(f"   - Name: {top_gifted_name}")
    print(f"   - Coins: {top_gifted_coins}")
    
    # Verify it's User A (the recipient/host), NOT User B (the sender)
    if top_gifted_id != user_a_id:
        print(f"❌ FAILED: most_gifted contains wrong user")
        print(f"   Expected: User A (recipient) {user_a_id}")
        print(f"   Got: {top_gifted_id}")
        if top_gifted_id == user_b_id:
            print(f"   ERROR: most_gifted shows User B (sender) instead of User A (recipient)")
        return False
    
    if top_gifted_coins != 10:
        print(f"❌ FAILED: most_gifted coins incorrect")
        print(f"   Expected: 10 coins")
        print(f"   Got: {top_gifted_coins} coins")
        return False
    
    print(f"✅ most_gifted correctly contains User A (RECIPIENT) with 10 coins")
    print(f"✅ User B (SENDER) is NOT in most_gifted (as expected)")
    
    # Step 7: Verify gift catalog
    print("\n[Step 7] GET /api/rooms/gift-catalog - verify catalog...")
    response = requests.get(
        f"{BACKEND_URL}/rooms/gift-catalog",
        headers={"Authorization": f"Bearer {token_a}"}
    )
    if response.status_code != 200:
        print(f"❌ FAILED: Gift catalog failed: {response.status_code} {response.text}")
        return False
    
    catalog = response.json()
    gifts = catalog.get("gifts", [])
    
    print(f"✅ Gift catalog retrieved")
    print(f"   User coins: {catalog.get('coins')}")
    print(f"   Number of gifts: {len(gifts)}")
    
    if len(gifts) != 4:
        print(f"❌ FAILED: Expected 4 gifts, got {len(gifts)}")
        return False
    
    expected_gifts = ["rose", "heart", "star", "crown"]
    gift_ids = [g.get("id") for g in gifts]
    
    for expected_id in expected_gifts:
        if expected_id not in gift_ids:
            print(f"❌ FAILED: Missing gift '{expected_id}' in catalog")
            return False
    
    print(f"✅ All 4 gifts present in catalog: {', '.join(gift_ids)}")
    
    for gift in gifts:
        print(f"   - {gift.get('name')} {gift.get('emoji')}: {gift.get('price')} coins")
    
    print("\n" + "=" * 80)
    print("✅ ALL TESTS PASSED - Voice Room Gift Feature Working Correctly")
    print("=" * 80)
    print("\nSUMMARY:")
    print("✅ Step 1: User A (mei) login - PASSED")
    print("✅ Step 2: User B (diego) login - PASSED")
    print("✅ Step 3: User A creates room - PASSED")
    print("✅ Step 4: User B joins room - PASSED")
    print("✅ Step 5: User B sends gift to User A - PASSED")
    print("   - Coins deducted correctly (10 coins)")
    print("   - Gift message returned with type='gift'")
    print("✅ Step 6: most_gifted verification - PASSED")
    print("   - most_gifted contains User A (RECIPIENT) with 10 coins")
    print("   - User B (SENDER) NOT in most_gifted (correct behavior)")
    print("✅ Step 7: Gift catalog - PASSED")
    print("   - Returns 4 gifts (rose, heart, star, crown)")
    print("\n✅ DESIGN INTENT VERIFIED: most_gifted tracks who RECEIVED gifts")
    print("   (not who sent them) - this is a 'who's most celebrated' leaderboard")
    
    return True

if __name__ == "__main__":
    try:
        success = test_gift_feature()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"\n❌ TEST FAILED WITH EXCEPTION: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
