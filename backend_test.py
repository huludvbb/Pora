#!/usr/bin/env python3
"""
Round 16 Backend Testing
Tests for:
A) Room create with announcement + background
B) Shared room card matches voice-tab shape (via moments)
C) Shared room card via chat message
D) Moment tag sanitization
E) Tag limit (9+ tags rejected)
F) Announcement length limit
G) Backward compatibility
"""

import requests
import sys
from datetime import datetime

# Backend URL from frontend/.env
BASE_URL = "https://23e89f0c-4dcc-40fe-82d2-2e242a0a0207.preview.emergentagent.com/api"

# Test credentials
MEI_EMAIL = "mei@demo.com"
MEI_PASSWORD = "Demo1234!"
DIEGO_EMAIL = "diego@demo.com"
DIEGO_PASSWORD = "Demo1234!"

def login(email, password):
    """Login and return token + user data"""
    resp = requests.post(f"{BASE_URL}/auth/login", json={"email": email, "password": password})
    if resp.status_code != 200:
        print(f"❌ Login failed for {email}: {resp.status_code} {resp.text}")
        return None, None
    data = resp.json()
    return data.get("token"), data.get("user")

def test_a_room_create_with_announcement_background():
    """A) Room create with announcement + background"""
    print("\n" + "="*80)
    print("TEST A: Room create with announcement + background")
    print("="*80)
    
    token, mei_user = login(MEI_EMAIL, MEI_PASSWORD)
    if not token:
        return False
    
    headers = {"Authorization": f"Bearer {token}"}
    
    # 1. Create room with announcement and background
    room_data = {
        "title": "Card Match Test",
        "language": "en",
        "topic": "General",
        "mode": "chat",
        "is_private": False,
        "background": 2,
        "announcement": "Please be kind ✨"
    }
    
    resp = requests.post(f"{BASE_URL}/rooms", json=room_data, headers=headers)
    print(f"\n1. POST /api/rooms → {resp.status_code}")
    
    if resp.status_code != 201:
        print(f"   ❌ Expected 201, got {resp.status_code}")
        print(f"   Response: {resp.text}")
        return False
    
    room = resp.json()
    room_id = room.get("id")
    
    # 2. Verify response fields
    print(f"\n2. Verify response fields:")
    
    announcement = room.get("announcement")
    print(f"   - announcement: {repr(announcement)}")
    if announcement != "Please be kind ✨":
        print(f"   ❌ Expected 'Please be kind ✨', got {repr(announcement)}")
        return False
    print(f"   ✅ announcement matches")
    
    background = room.get("background")
    print(f"   - background: {background}")
    if background != 2:
        print(f"   ❌ Expected 2, got {background}")
        return False
    print(f"   ✅ background matches")
    
    host = room.get("host")
    print(f"   - host: {host}")
    if not host:
        print(f"   ❌ host is missing")
        return False
    
    if not host.get("id"):
        print(f"   ❌ host.id is missing")
        return False
    
    if not host.get("name"):
        print(f"   ❌ host.name is missing")
        return False
    
    if "avatar_url" not in host:
        print(f"   ❌ host.avatar_url is missing")
        return False
    
    print(f"   ✅ host contains id, name, avatar_url")
    
    print(f"\n✅ TEST A PASSED")
    return room_id

def test_b_shared_room_card_via_moments(room_id):
    """B) Shared room card matches voice-tab shape (via moments)"""
    print("\n" + "="*80)
    print("TEST B: Shared room card matches voice-tab shape (via moments)")
    print("="*80)
    
    diego_token, diego_user = login(DIEGO_EMAIL, DIEGO_PASSWORD)
    if not diego_token:
        return False
    
    diego_headers = {"Authorization": f"Bearer {diego_token}"}
    
    # 1. Diego joins room
    resp = requests.post(f"{BASE_URL}/rooms/{room_id}/join", headers=diego_headers)
    print(f"\n1. POST /api/rooms/{room_id}/join → {resp.status_code}")
    
    if resp.status_code != 200:
        print(f"   ❌ Expected 200, got {resp.status_code}")
        print(f"   Response: {resp.text}")
        return False
    print(f"   ✅ Diego joined room")
    
    # 2. Diego shares room to moments
    share_data = {"text": "Come join"}
    resp = requests.post(f"{BASE_URL}/rooms/{room_id}/share-to-moments", json=share_data, headers=diego_headers)
    print(f"\n2. POST /api/rooms/{room_id}/share-to-moments → {resp.status_code}")
    
    if resp.status_code != 201:
        print(f"   ❌ Expected 201, got {resp.status_code}")
        print(f"   Response: {resp.text}")
        return False
    print(f"   ✅ Room shared to moments")
    
    # 3. Get moments as Diego and find the shared room
    resp = requests.get(f"{BASE_URL}/moments", headers=diego_headers)
    print(f"\n3. GET /api/moments → {resp.status_code}")
    
    if resp.status_code != 200:
        print(f"   ❌ Expected 200, got {resp.status_code}")
        return False
    
    moments = resp.json()
    
    # Find moment with text "Come join"
    target_moment = None
    for m in moments:
        if m.get("text") == "Come join":
            target_moment = m
            break
    
    if not target_moment:
        print(f"   ❌ Could not find moment with text 'Come join'")
        print(f"   Found {len(moments)} moments")
        return False
    
    print(f"   ✅ Found moment with text 'Come join'")
    
    # 4. Verify moment.room contains required fields
    print(f"\n4. Verify moment.room shape:")
    
    room = target_moment.get("room")
    if not room:
        print(f"   ❌ moment.room is missing")
        return False
    
    # Required fields
    required_fields = {
        "id": str,
        "title": str,
        "is_live": bool,
        "background": int,
        "topic": str,
        "is_private": bool,
        "language": str,
        "created_at": str,
        "member_count": int,
        "host": dict,
        "members_preview": list
    }
    
    for field, expected_type in required_fields.items():
        value = room.get(field)
        if value is None and field not in room:
            print(f"   ❌ room.{field} is missing")
            return False
        if value is not None and not isinstance(value, expected_type):
            print(f"   ❌ room.{field} has wrong type: expected {expected_type}, got {type(value)}")
            return False
        print(f"   ✅ room.{field} = {repr(value)[:80]}")
    
    # Verify specific values
    if room.get("title") != "Card Match Test":
        print(f"   ❌ Expected title 'Card Match Test', got {repr(room.get('title'))}")
        return False
    
    if room.get("is_live") != True:
        print(f"   ❌ Expected is_live=true, got {room.get('is_live')}")
        return False
    
    if room.get("background") != 2:
        print(f"   ❌ Expected background=2, got {room.get('background')}")
        return False
    
    if room.get("topic") != "General":
        print(f"   ❌ Expected topic='General', got {repr(room.get('topic'))}")
        return False
    
    if room.get("is_private") != False:
        print(f"   ❌ Expected is_private=false, got {room.get('is_private')}")
        return False
    
    if room.get("language") != "en":
        print(f"   ❌ Expected language='en', got {repr(room.get('language'))}")
        return False
    
    if room.get("member_count") < 2:
        print(f"   ❌ Expected member_count >= 2, got {room.get('member_count')}")
        return False
    
    # Verify host object
    host = room.get("host")
    if not host:
        print(f"   ❌ room.host is missing")
        return False
    
    mei_token, mei_user = login(MEI_EMAIL, MEI_PASSWORD)
    mei_id = mei_user.get("id")
    
    if host.get("id") != mei_id:
        print(f"   ❌ Expected host.id={mei_id}, got {host.get('id')}")
        return False
    
    if not host.get("name"):
        print(f"   ❌ host.name is missing")
        return False
    
    if "avatar_url" not in host:
        print(f"   ❌ host.avatar_url is missing")
        return False
    
    if "country" not in host:
        print(f"   ❌ host.country is missing")
        return False
    
    print(f"   ✅ host object complete (id, name, avatar_url, country)")
    
    # Verify members_preview
    members_preview = room.get("members_preview")
    if not isinstance(members_preview, list):
        print(f"   ❌ members_preview is not a list")
        return False
    
    if len(members_preview) < 2:
        print(f"   ❌ Expected at least 2 members in preview, got {len(members_preview)}")
        return False
    
    # Check that members have id, name, avatar_url
    for i, member in enumerate(members_preview[:2]):
        if not member.get("id"):
            print(f"   ❌ members_preview[{i}].id is missing")
            return False
        if not member.get("name"):
            print(f"   ❌ members_preview[{i}].name is missing")
            return False
        if "avatar_url" not in member:
            print(f"   ❌ members_preview[{i}].avatar_url is missing")
            return False
    
    print(f"   ✅ members_preview contains at least 2 members with id/name/avatar_url")
    
    print(f"\n✅ TEST B PASSED")
    return True

def test_c_shared_room_card_via_chat(room_id):
    """C) Shared room card via chat message"""
    print("\n" + "="*80)
    print("TEST C: Shared room card via chat message")
    print("="*80)
    
    mei_token, mei_user = login(MEI_EMAIL, MEI_PASSWORD)
    diego_token, diego_user = login(DIEGO_EMAIL, DIEGO_PASSWORD)
    
    if not mei_token or not diego_token:
        return False
    
    mei_headers = {"Authorization": f"Bearer {mei_token}"}
    diego_id = diego_user.get("id")
    mei_id = mei_user.get("id")
    
    # 1. Mei creates/finds conversation with Diego
    conv_data = {"partner_id": diego_id}
    resp = requests.post(f"{BASE_URL}/chats", json=conv_data, headers=mei_headers)
    print(f"\n1. POST /api/chats (partner_id={diego_id}) → {resp.status_code}")
    
    if resp.status_code != 200:
        print(f"   ❌ Expected 200, got {resp.status_code}")
        print(f"   Response: {resp.text}")
        return False
    
    conv = resp.json()
    conv_id = conv.get("id")
    print(f"   ✅ Conversation ID: {conv_id}")
    
    # 2. Mei sends room share message
    msg_data = {"room_id": room_id}
    resp = requests.post(f"{BASE_URL}/chats/{conv_id}/messages", json=msg_data, headers=mei_headers)
    print(f"\n2. POST /api/chats/{conv_id}/messages (room_id={room_id}) → {resp.status_code}")
    
    if resp.status_code != 201:
        print(f"   ❌ Expected 201, got {resp.status_code}")
        print(f"   Response: {resp.text}")
        return False
    
    msg = resp.json()
    print(f"   ✅ Room share message created")
    
    # 3. Get messages and verify last message has room card
    resp = requests.get(f"{BASE_URL}/chats/{conv_id}/messages", headers=mei_headers)
    print(f"\n3. GET /api/chats/{conv_id}/messages → {resp.status_code}")
    
    if resp.status_code != 200:
        print(f"   ❌ Expected 200, got {resp.status_code}")
        return False
    
    messages = resp.json()
    if not messages:
        print(f"   ❌ No messages found")
        return False
    
    last_msg = messages[-1]
    
    # Verify message type
    if last_msg.get("type") != "room":
        print(f"   ❌ Expected type='room', got {repr(last_msg.get('type'))}")
        return False
    print(f"   ✅ Message type is 'room'")
    
    # Verify room field
    print(f"\n4. Verify message.room shape:")
    
    room = last_msg.get("room")
    if not room:
        print(f"   ❌ message.room is missing")
        return False
    
    # Same shape as moments room card
    required_fields = {
        "id": str,
        "title": str,
        "is_live": bool,
        "background": int,
        "topic": str,
        "is_private": bool,
        "language": str,
        "created_at": str,
        "member_count": int,
        "host": dict,
        "members_preview": list
    }
    
    for field, expected_type in required_fields.items():
        value = room.get(field)
        if value is None and field not in room:
            print(f"   ❌ room.{field} is missing")
            return False
        if value is not None and not isinstance(value, expected_type):
            print(f"   ❌ room.{field} has wrong type: expected {expected_type}, got {type(value)}")
            return False
        print(f"   ✅ room.{field} = {repr(value)[:80]}")
    
    # Verify host object
    host = room.get("host")
    if not host or not host.get("id") or not host.get("name") or "avatar_url" not in host:
        print(f"   ❌ host object incomplete")
        return False
    print(f"   ✅ host object complete")
    
    # Verify members_preview
    members_preview = room.get("members_preview")
    if not isinstance(members_preview, list) or len(members_preview) < 2:
        print(f"   ❌ members_preview should have at least 2 members")
        return False
    print(f"   ✅ members_preview has {len(members_preview)} members")
    
    print(f"\n✅ TEST C PASSED")
    return True

def test_d_moment_tag_sanitization():
    """D) Moment tag sanitization"""
    print("\n" + "="*80)
    print("TEST D: Moment tag sanitization")
    print("="*80)
    
    mei_token, mei_user = login(MEI_EMAIL, MEI_PASSWORD)
    if not mei_token:
        return False
    
    mei_headers = {"Authorization": f"Bearer {mei_token}"}
    
    # 1. Create moment with various tag formats
    tags_input = ["language", "#Grammar", "Studying_Hard", "  ", "meet@new"]
    moment_data = {
        "text": "Hi",
        "tags": tags_input
    }
    
    resp = requests.post(f"{BASE_URL}/moments", json=moment_data, headers=mei_headers)
    print(f"\n1. POST /api/moments with tags={tags_input} → {resp.status_code}")
    
    if resp.status_code != 201:
        print(f"   ❌ Expected 201, got {resp.status_code}")
        print(f"   Response: {resp.text}")
        return False
    
    moment = resp.json()
    moment_id = moment.get("id")
    
    # 2. Verify response.tags
    tags_output = moment.get("tags")
    expected_tags = ["language", "grammar", "studying_hard", "meetnew"]
    
    print(f"\n2. Verify tag sanitization:")
    print(f"   Input:    {tags_input}")
    print(f"   Output:   {tags_output}")
    print(f"   Expected: {expected_tags}")
    
    if tags_output != expected_tags:
        print(f"   ❌ Tags don't match expected output")
        print(f"   Expected: {expected_tags}")
        print(f"   Got:      {tags_output}")
        return False
    
    print(f"   ✅ Tag sanitization correct:")
    print(f"      - 'language' → 'language' (unchanged)")
    print(f"      - '#Grammar' → 'grammar' (# stripped, lowercase)")
    print(f"      - 'Studying_Hard' → 'studying_hard' (lowercase, underscore kept)")
    print(f"      - '  ' → dropped (empty after strip)")
    print(f"      - 'meet@new' → 'meetnew' (@ stripped)")
    
    # 3. Verify via GET /api/moments
    resp = requests.get(f"{BASE_URL}/moments", headers=mei_headers)
    print(f"\n3. GET /api/moments → {resp.status_code}")
    
    if resp.status_code != 200:
        print(f"   ❌ Expected 200, got {resp.status_code}")
        return False
    
    moments = resp.json()
    found_moment = None
    for m in moments:
        if m.get("id") == moment_id:
            found_moment = m
            break
    
    if not found_moment:
        print(f"   ❌ Could not find moment with id={moment_id}")
        return False
    
    if found_moment.get("tags") != expected_tags:
        print(f"   ❌ Tags in GET response don't match")
        print(f"   Expected: {expected_tags}")
        print(f"   Got:      {found_moment.get('tags')}")
        return False
    
    print(f"   ✅ Tags persist correctly in GET response")
    
    print(f"\n✅ TEST D PASSED")
    return True

def test_e_tag_limit():
    """E) Tag limit (9+ tags rejected)"""
    print("\n" + "="*80)
    print("TEST E: Tag limit (9+ tags rejected)")
    print("="*80)
    
    mei_token, mei_user = login(MEI_EMAIL, MEI_PASSWORD)
    if not mei_token:
        return False
    
    mei_headers = {"Authorization": f"Bearer {mei_token}"}
    
    # Try to create moment with 9 tags (should fail with 422)
    tags_input = ["a", "b", "c", "d", "e", "f", "g", "h", "i"]
    moment_data = {
        "text": "too many",
        "tags": tags_input
    }
    
    resp = requests.post(f"{BASE_URL}/moments", json=moment_data, headers=mei_headers)
    print(f"\n1. POST /api/moments with 9 tags → {resp.status_code}")
    print(f"   Tags: {tags_input}")
    
    if resp.status_code != 422:
        print(f"   ❌ Expected 422 (validation error), got {resp.status_code}")
        print(f"   Response: {resp.text}")
        return False
    
    print(f"   ✅ 9 tags correctly rejected with 422 (Pydantic max_length validation)")
    
    print(f"\n✅ TEST E PASSED")
    return True

def test_f_announcement_length_limit():
    """F) Announcement length limit"""
    print("\n" + "="*80)
    print("TEST F: Announcement length limit")
    print("="*80)
    
    mei_token, mei_user = login(MEI_EMAIL, MEI_PASSWORD)
    if not mei_token:
        return False
    
    mei_headers = {"Authorization": f"Bearer {mei_token}"}
    
    # Try to create room with 400-char announcement (max is 300)
    long_announcement = "a" * 400
    room_data = {
        "title": "Test Room",
        "language": "en",
        "announcement": long_announcement
    }
    
    resp = requests.post(f"{BASE_URL}/rooms", json=room_data, headers=mei_headers)
    print(f"\n1. POST /api/rooms with 400-char announcement → {resp.status_code}")
    print(f"   Announcement length: {len(long_announcement)} chars (max is 300)")
    
    if resp.status_code != 422:
        print(f"   ❌ Expected 422 (validation error), got {resp.status_code}")
        print(f"   Response: {resp.text}")
        return False
    
    print(f"   ✅ 400-char announcement correctly rejected with 422 (Pydantic max_length validation)")
    
    print(f"\n✅ TEST F PASSED")
    return True

def test_g_backward_compatibility():
    """G) Backward compatibility"""
    print("\n" + "="*80)
    print("TEST G: Backward compatibility")
    print("="*80)
    
    mei_token, mei_user = login(MEI_EMAIL, MEI_PASSWORD)
    if not mei_token:
        return False
    
    mei_headers = {"Authorization": f"Bearer {mei_token}"}
    
    # 1. Create moment without tags
    moment_data = {"text": "plain post"}
    resp = requests.post(f"{BASE_URL}/moments", json=moment_data, headers=mei_headers)
    print(f"\n1. POST /api/moments without tags → {resp.status_code}")
    
    if resp.status_code != 201:
        print(f"   ❌ Expected 201, got {resp.status_code}")
        print(f"   Response: {resp.text}")
        return False
    
    moment = resp.json()
    tags = moment.get("tags")
    
    if tags != []:
        print(f"   ❌ Expected tags=[], got {repr(tags)}")
        return False
    
    print(f"   ✅ Moment without tags returns tags=[]")
    
    # 2. Create room without announcement
    room_data = {
        "title": "No Announcement Room",
        "language": "en"
    }
    resp = requests.post(f"{BASE_URL}/rooms", json=room_data, headers=mei_headers)
    print(f"\n2. POST /api/rooms without announcement → {resp.status_code}")
    
    if resp.status_code != 201:
        print(f"   ❌ Expected 201, got {resp.status_code}")
        print(f"   Response: {resp.text}")
        return False
    
    room = resp.json()
    announcement = room.get("announcement")
    
    if announcement is not None:
        print(f"   ❌ Expected announcement=null, got {repr(announcement)}")
        return False
    
    print(f"   ✅ Room without announcement returns announcement=null")
    
    print(f"\n✅ TEST G PASSED")
    return True

def main():
    print("\n" + "="*80)
    print("ROUND 16 BACKEND TESTING")
    print("="*80)
    print(f"Backend URL: {BASE_URL}")
    print(f"Test users: {MEI_EMAIL}, {DIEGO_EMAIL}")
    
    results = {}
    
    # Test A: Room create with announcement + background
    room_id = test_a_room_create_with_announcement_background()
    results["A"] = bool(room_id)
    
    if room_id:
        # Test B: Shared room card via moments
        results["B"] = test_b_shared_room_card_via_moments(room_id)
        
        # Test C: Shared room card via chat
        results["C"] = test_c_shared_room_card_via_chat(room_id)
    else:
        results["B"] = False
        results["C"] = False
    
    # Test D: Moment tag sanitization
    results["D"] = test_d_moment_tag_sanitization()
    
    # Test E: Tag limit
    results["E"] = test_e_tag_limit()
    
    # Test F: Announcement length limit
    results["F"] = test_f_announcement_length_limit()
    
    # Test G: Backward compatibility
    results["G"] = test_g_backward_compatibility()
    
    # Summary
    print("\n" + "="*80)
    print("SUMMARY")
    print("="*80)
    
    passed = sum(1 for v in results.values() if v)
    total = len(results)
    
    for test, result in results.items():
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"Test {test}: {status}")
    
    print(f"\nTotal: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 ALL TESTS PASSED!")
        return 0
    else:
        print(f"\n⚠️  {total - passed} test(s) failed")
        return 1

if __name__ == "__main__":
    sys.exit(main())
