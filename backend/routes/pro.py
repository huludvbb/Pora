"""
Pro — a 1-on-1 video language-tutoring sub-app that lives inside the main
LinguaConnect app. No auth of its own: it maps everything to the already
logged-in user (their user id acts as the `external_user_id`).

Entities (kept lightweight in Mongo):
  - LanguageProfile  -> pro_profiles       (one per external_user_id)
  - LessonSession    -> pro_sessions
  - SessionTranscript-> pro_transcripts
  - LessonWallet     -> pro_wallets
  - Availability     -> pro_availability    (tutor open teaching blocks)
"""

import uuid
from datetime import datetime, timezone
from typing import List, Optional

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from auth_utils import CurrentUser
from db import (
    pro_availability_col,
    pro_profiles_col,
    pro_sessions_col,
    pro_transcripts_col,
    pro_wallets_col,
)

router = APIRouter(prefix="/pro", tags=["pro"])


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


# --------------------------------------------------------------------------- #
# Serializers
# --------------------------------------------------------------------------- #
def profile_public(d: dict) -> dict:
    return {
        "id": d["_id"],
        "external_user_id": d.get("external_user_id"),
        "role": d.get("role", "student"),
        "name": d.get("name"),
        "bio": d.get("bio", ""),
        "avatar_url": d.get("avatar_url"),
        "video_intro_url": d.get("video_intro_url"),
        "native_accent": d.get("native_accent"),
        "teaches": d.get("teaches", []),
        "specialties": d.get("specialties", []),
        "languages": d.get("languages", []),
        "hourly_rate": d.get("hourly_rate", 0),
        "rating": d.get("rating", 0),
        "reviews_count": d.get("reviews_count", 0),
        "lessons_taught": d.get("lessons_taught", 0),
        "is_online": d.get("is_online", False),
        "country": d.get("country"),
        "featured": d.get("featured", False),
    }


def session_public(d: dict) -> dict:
    return {
        "id": d["_id"],
        "student_profile_id": d.get("student_profile_id"),
        "tutor_profile_id": d.get("tutor_profile_id"),
        "student": d.get("student"),
        "tutor": d.get("tutor"),
        "status": d.get("status"),
        "start_time": d.get("start_time"),
        "end_time": d.get("end_time"),
        "call_duration": d.get("call_duration", 0),
        "stream_room_token": d.get("stream_room_token"),
        "created_at": d.get("created_at"),
    }


# --------------------------------------------------------------------------- #
# Profile helpers
# --------------------------------------------------------------------------- #
async def _ensure_profile(user: dict) -> dict:
    """Return the LanguageProfile for a main-app user, creating a default
    student profile on first access (idempotent)."""
    uid = user["_id"]
    prof = await pro_profiles_col.find_one({"external_user_id": uid})
    if prof:
        return prof
    doc = {
        "_id": str(uuid.uuid4()),
        "external_user_id": uid,
        "role": "student",
        "name": user.get("name") or "Learner",
        "bio": user.get("bio", ""),
        "avatar_url": user.get("avatar_url"),
        "video_intro_url": None,
        "native_accent": None,
        "teaches": [],
        "specialties": [],
        "languages": [user.get("learning_language")] if user.get("learning_language") else [],
        "hourly_rate": 0,
        "rating": 0,
        "reviews_count": 0,
        "lessons_taught": 0,
        "is_online": True,
        "country": user.get("country"),
        "featured": False,
        "created_at": _now(),
    }
    await pro_profiles_col.insert_one(doc)
    await _ensure_wallet(doc["_id"])
    return doc


async def _ensure_wallet(profile_id: str) -> dict:
    w = await pro_wallets_col.find_one({"profile_id": profile_id})
    if w:
        return w
    doc = {
        "_id": str(uuid.uuid4()),
        "profile_id": profile_id,
        "balance": 60,  # 60 free trial minutes for new learners
        "currency": "MIN",  # minutes-based wallet
        "created_at": _now(),
    }
    await pro_wallets_col.insert_one(doc)
    return doc


# --------------------------------------------------------------------------- #
# Request models
# --------------------------------------------------------------------------- #
class ProfileUpdate(BaseModel):
    bio: Optional[str] = None
    native_accent: Optional[str] = None
    teaches: Optional[List[str]] = None
    specialties: Optional[List[str]] = None
    languages: Optional[List[str]] = None
    hourly_rate: Optional[float] = None
    video_intro_url: Optional[str] = None


class RoleUpdate(BaseModel):
    role: str = Field(..., pattern="^(student|tutor)$")


class MatchRequest(BaseModel):
    language: Optional[str] = None
    tutor_id: Optional[str] = None  # book a specific tutor (else instant match)


class AvailabilityUpdate(BaseModel):
    # list of blocks like {"day": 0-6, "start": "09:00", "end": "12:00"}
    blocks: List[dict]


# --------------------------------------------------------------------------- #
# Profile / role
# --------------------------------------------------------------------------- #
@router.get("/me")
async def get_me(current_user: CurrentUser):
    prof = await _ensure_profile(current_user)
    wallet = await _ensure_wallet(prof["_id"])
    return {
        "profile": profile_public(prof),
        "wallet": {"balance": wallet["balance"], "currency": wallet["currency"]},
    }


@router.put("/me")
async def update_me(body: ProfileUpdate, current_user: CurrentUser):
    prof = await _ensure_profile(current_user)
    updates = {k: v for k, v in body.model_dump().items() if v is not None}
    if updates:
        await pro_profiles_col.update_one({"_id": prof["_id"]}, {"$set": updates})
    prof = await pro_profiles_col.find_one({"_id": prof["_id"]})
    return profile_public(prof)


@router.post("/role")
async def set_role(body: RoleUpdate, current_user: CurrentUser):
    prof = await _ensure_profile(current_user)
    await pro_profiles_col.update_one(
        {"_id": prof["_id"]}, {"$set": {"role": body.role}}
    )
    prof = await pro_profiles_col.find_one({"_id": prof["_id"]})
    return profile_public(prof)


# --------------------------------------------------------------------------- #
# Tutors
# --------------------------------------------------------------------------- #
@router.get("/tutors")
async def list_tutors(language: Optional[str] = None, q: Optional[str] = None):
    query: dict = {"role": "tutor"}
    if language:
        query["teaches"] = language
    cursor = pro_profiles_col.find(query)
    tutors = [profile_public(d) async for d in cursor]
    if q:
        ql = q.lower()
        tutors = [
            t
            for t in tutors
            if ql in (t["name"] or "").lower()
            or ql in (t["bio"] or "").lower()
            or any(ql in s.lower() for s in t["specialties"])
        ]
    # Featured + higher rating first, then online.
    tutors.sort(
        key=lambda t: (t["featured"], t["is_online"], t["rating"]), reverse=True
    )
    return tutors


@router.get("/tutors/{tutor_id}")
async def tutor_detail(tutor_id: str):
    d = await pro_profiles_col.find_one({"_id": tutor_id, "role": "tutor"})
    if not d:
        raise HTTPException(status_code=404, detail="Tutor not found")
    return profile_public(d)


# --------------------------------------------------------------------------- #
# Matchmaking + sessions
# --------------------------------------------------------------------------- #
@router.post("/match")
async def match(body: MatchRequest, current_user: CurrentUser):
    student = await _ensure_profile(current_user)

    tutor = None
    if body.tutor_id:
        tutor = await pro_profiles_col.find_one(
            {"_id": body.tutor_id, "role": "tutor"}
        )
        if not tutor:
            raise HTTPException(status_code=404, detail="Tutor not found")
    else:
        # Instant match: prefer an online tutor for the requested language.
        query: dict = {"role": "tutor", "is_online": True}
        if body.language:
            query["teaches"] = body.language
        tutor = await pro_profiles_col.find_one(query)
        if not tutor and body.language:
            tutor = await pro_profiles_col.find_one(
                {"role": "tutor", "teaches": body.language}
            )
        if not tutor:
            tutor = await pro_profiles_col.find_one({"role": "tutor"})
    if not tutor:
        raise HTTPException(status_code=503, detail="No tutors available right now")

    session = {
        "_id": str(uuid.uuid4()),
        "student_profile_id": student["_id"],
        "tutor_profile_id": tutor["_id"],
        "student": profile_public(student),
        "tutor": profile_public(tutor),
        "status": "active",
        "start_time": _now(),
        "end_time": None,
        "call_duration": 0,
        "stream_room_token": str(uuid.uuid4()),
        "created_at": _now(),
    }
    await pro_sessions_col.insert_one(session)
    return session_public(session)


@router.get("/sessions")
async def my_sessions(current_user: CurrentUser):
    prof = await _ensure_profile(current_user)
    cursor = pro_sessions_col.find(
        {
            "$or": [
                {"student_profile_id": prof["_id"]},
                {"tutor_profile_id": prof["_id"]},
            ]
        }
    ).sort("created_at", -1)
    return [session_public(d) async for d in cursor]


@router.get("/sessions/{session_id}")
async def session_detail(session_id: str, current_user: CurrentUser):
    prof = await _ensure_profile(current_user)
    d = await pro_sessions_col.find_one({"_id": session_id})
    if not d:
        raise HTTPException(status_code=404, detail="Session not found")
    if prof["_id"] not in (d.get("student_profile_id"), d.get("tutor_profile_id")):
        raise HTTPException(status_code=403, detail="Not your session")
    return session_public(d)


@router.post("/sessions/{session_id}/end")
async def end_session(session_id: str, current_user: CurrentUser):
    prof = await _ensure_profile(current_user)
    d = await pro_sessions_col.find_one({"_id": session_id})
    if not d:
        raise HTTPException(status_code=404, detail="Session not found")
    if prof["_id"] not in (d.get("student_profile_id"), d.get("tutor_profile_id")):
        raise HTTPException(status_code=403, detail="Not your session")
    if d.get("status") == "completed":
        return session_public(d)
    start = d.get("start_time")
    duration = 0
    try:
        started = datetime.fromisoformat(start)
        duration = int((datetime.now(timezone.utc) - started).total_seconds())
    except Exception:
        duration = 0
    await pro_sessions_col.update_one(
        {"_id": session_id},
        {
            "$set": {
                "status": "completed",
                "end_time": _now(),
                "call_duration": duration,
            }
        },
    )
    # Count a lesson taught for the tutor.
    await pro_profiles_col.update_one(
        {"_id": d["tutor_profile_id"]}, {"$inc": {"lessons_taught": 1}}
    )
    d = await pro_sessions_col.find_one({"_id": session_id})
    return session_public(d)


# --------------------------------------------------------------------------- #
# Wallet
# --------------------------------------------------------------------------- #
@router.get("/wallet")
async def get_wallet(current_user: CurrentUser):
    prof = await _ensure_profile(current_user)
    w = await _ensure_wallet(prof["_id"])
    return {"balance": w["balance"], "currency": w["currency"]}


# --------------------------------------------------------------------------- #
# Progress (aggregated stats for the Progress tab)
# --------------------------------------------------------------------------- #
@router.get("/progress")
async def progress(current_user: CurrentUser):
    prof = await _ensure_profile(current_user)
    completed = pro_sessions_col.find(
        {"student_profile_id": prof["_id"], "status": "completed"}
    )
    total_seconds = 0
    lessons = 0
    tutors = set()
    async for s in completed:
        total_seconds += s.get("call_duration", 0)
        lessons += 1
        tutors.add(s.get("tutor_profile_id"))
    return {
        "lessons_completed": lessons,
        "minutes_practiced": round(total_seconds / 60),
        "tutors_met": len(tutors),
        # A simple 7-day streak seed so the UI has something meaningful.
        "day_streak": min(lessons, 7),
        "words_learned": lessons * 12,
    }


# --------------------------------------------------------------------------- #
# Tutor availability
# --------------------------------------------------------------------------- #
@router.get("/availability")
async def get_availability(current_user: CurrentUser):
    prof = await _ensure_profile(current_user)
    doc = await pro_availability_col.find_one({"profile_id": prof["_id"]})
    return {"blocks": (doc or {}).get("blocks", [])}


@router.put("/availability")
async def set_availability(body: AvailabilityUpdate, current_user: CurrentUser):
    prof = await _ensure_profile(current_user)
    await pro_availability_col.update_one(
        {"profile_id": prof["_id"]},
        {"$set": {"blocks": body.blocks, "updated_at": _now()}},
        upsert=True,
    )
    return {"blocks": body.blocks}


# --------------------------------------------------------------------------- #
# Seed demo tutors (idempotent)
# --------------------------------------------------------------------------- #
DEMO_TUTORS = [
    {
        "name": "Eleanor Whitfield",
        "country": "gb",
        "native_accent": "British · RP Accent",
        "teaches": ["en"],
        "specialties": ["Business English", "IELTS", "Pronunciation"],
        "bio": "Cambridge-certified coach helping professionals speak with clarity and confidence.",
        "hourly_rate": 18,
        "rating": 4.9,
        "reviews_count": 412,
        "lessons_taught": 3800,
        "avatar_url": "https://i.pravatar.cc/300?img=47",
        "featured": True,
    },
    {
        "name": "Marcus Bennett",
        "country": "us",
        "native_accent": "American · General",
        "teaches": ["en"],
        "specialties": ["Conversation", "Interview Prep", "Slang"],
        "bio": "Relaxed, friendly sessions focused on real-world speaking and confidence.",
        "hourly_rate": 15,
        "rating": 4.8,
        "reviews_count": 289,
        "lessons_taught": 2600,
        "avatar_url": "https://i.pravatar.cc/300?img=12",
        "featured": True,
    },
    {
        "name": "Sofía Martínez",
        "country": "es",
        "native_accent": "Castilian Spanish",
        "teaches": ["es"],
        "specialties": ["Beginners", "Travel Spanish", "Grammar"],
        "bio": "Patient native Spanish teacher — perfect for beginners and travellers.",
        "hourly_rate": 14,
        "rating": 5.0,
        "reviews_count": 356,
        "lessons_taught": 3100,
        "avatar_url": "https://i.pravatar.cc/300?img=45",
        "featured": True,
    },
    {
        "name": "Kenji Tanaka",
        "country": "jp",
        "native_accent": "Standard Japanese",
        "teaches": ["ja"],
        "specialties": ["JLPT", "Keigo", "Business Japanese"],
        "bio": "Structured JLPT prep and natural conversation practice for all levels.",
        "hourly_rate": 20,
        "rating": 4.9,
        "reviews_count": 198,
        "lessons_taught": 1700,
        "avatar_url": "https://i.pravatar.cc/300?img=13",
        "featured": False,
    },
    {
        "name": "Amélie Laurent",
        "country": "fr",
        "native_accent": "Parisian French",
        "teaches": ["fr"],
        "specialties": ["DELF", "Conversation", "Culture"],
        "bio": "Bring French to life with culture-rich, engaging conversation lessons.",
        "hourly_rate": 17,
        "rating": 4.7,
        "reviews_count": 221,
        "lessons_taught": 1900,
        "avatar_url": "https://i.pravatar.cc/300?img=31",
        "featured": False,
    },
    {
        "name": "Liwei Chen",
        "country": "cn",
        "native_accent": "Mandarin · Beijing",
        "teaches": ["zh"],
        "specialties": ["HSK", "Pinyin", "Business Chinese"],
        "bio": "Clear, methodical Mandarin lessons from pinyin basics to fluent HSK 6.",
        "hourly_rate": 16,
        "rating": 4.8,
        "reviews_count": 174,
        "lessons_taught": 1500,
        "avatar_url": "https://i.pravatar.cc/300?img=33",
        "featured": False,
    },
    {
        "name": "Isabella Rossi",
        "country": "it",
        "native_accent": "Standard Italian",
        "teaches": ["it"],
        "specialties": ["Beginners", "Conversation", "Opera & Culture"],
        "bio": "Warm, expressive Italian lessons that make learning feel like a holiday.",
        "hourly_rate": 15,
        "rating": 4.9,
        "reviews_count": 143,
        "lessons_taught": 1200,
        "avatar_url": "https://i.pravatar.cc/300?img=48",
        "featured": False,
    },
    {
        "name": "James O'Connor",
        "country": "gb",
        "native_accent": "British · Irish lilt",
        "teaches": ["en"],
        "specialties": ["Academic Writing", "TOEFL", "Debate"],
        "bio": "Sharpen academic English and critical thinking with structured feedback.",
        "hourly_rate": 19,
        "rating": 4.8,
        "reviews_count": 267,
        "lessons_taught": 2400,
        "avatar_url": "https://i.pravatar.cc/300?img=52",
        "featured": False,
    },
]


async def seed_pro_tutors():
    """Idempotent — inserts the demo tutor roster once (keyed by synthetic id)."""
    for i, t in enumerate(DEMO_TUTORS):
        ext_id = f"pro-tutor-{i+1}"
        existing = await pro_profiles_col.find_one({"external_user_id": ext_id})
        doc = {
            "external_user_id": ext_id,
            "role": "tutor",
            "video_intro_url": None,
            "languages": t["teaches"],
            "is_online": i % 3 != 0,  # most online, a couple offline for realism
            **t,
        }
        if existing:
            # keep it fresh but don't reset dynamic counters weirdly
            await pro_profiles_col.update_one(
                {"_id": existing["_id"]}, {"$set": doc}
            )
        else:
            doc["_id"] = str(uuid.uuid4())
            doc["created_at"] = _now()
            await pro_profiles_col.insert_one(doc)
            await _ensure_wallet(doc["_id"])
