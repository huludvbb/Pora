"""Learn module — spaced-repetition vocabulary flashcards.

Design goals:
- Users pick a target language once (or reuse the one from onboarding).
- Get a daily set of ~20 words to review — mix of new + due cards.
- Each review is graded: `correct` / `hard` / `wrong`. The card's next review
  interval is scheduled by a simple SM-2-lite algorithm.
- Wrong answers land in a "Recent Mistakes" bucket so the user can drill them.
- Free-form "Custom Collections" (saved word lists) let users curate their own
  vocab groups.

All data lives in three mongo collections created lazily by the server
startup helper: `learn_vocab` (canonical curated vocab), `learn_user_cards`
(one row per user × word pair with schedule), and `learn_collections`
(user-owned saved lists).
"""

from __future__ import annotations

import uuid
from datetime import datetime, timedelta, timezone
from typing import Optional

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from auth_utils import CurrentUser
from db import db  # motor client shortcut

router = APIRouter(prefix="/learn", tags=["learn"])

vocab_col = db["learn_vocab"]
cards_col = db["learn_user_cards"]
collections_col = db["learn_collections"]


# Seed vocabulary — small curated set per language to bootstrap the experience.
# Real product would ingest CEFR word lists; here we keep it tight so a fresh
# user immediately sees content on first open.
SEED_VOCAB = {
    "en": [
        ("Serendipity", "The occurrence of finding something pleasant by chance.", "beginner"),
        ("Eloquent", "Fluent, persuasive and effective in speaking or writing.", "intermediate"),
        ("Resilient", "Able to recover quickly from difficulties.", "beginner"),
        ("Nostalgic", "Feeling sentimental affection for the past.", "intermediate"),
        ("Ephemeral", "Lasting for a very short time.", "advanced"),
        ("Vivid", "Producing powerful feelings or strong, clear images.", "beginner"),
        ("Curiosity", "A strong desire to know or learn something.", "beginner"),
        ("Humble", "Having or showing a modest estimate of one's own importance.", "beginner"),
        ("Ambitious", "Having a strong desire and determination to succeed.", "beginner"),
        ("Adventure", "An unusual and exciting or daring experience.", "beginner"),
        ("Journey", "An act of traveling from one place to another.", "beginner"),
        ("Perspective", "A particular attitude toward or way of regarding something.", "intermediate"),
    ],
    "es": [
        ("Bienvenido", "Welcome — used to greet arrivals.", "beginner"),
        ("Amistad", "Friendship.", "beginner"),
        ("Aventura", "Adventure.", "beginner"),
        ("Sonrisa", "Smile.", "beginner"),
        ("Esperanza", "Hope.", "beginner"),
        ("Aprender", "To learn.", "beginner"),
        ("Recuerdo", "Memory / souvenir.", "intermediate"),
        ("Amanecer", "Sunrise / to dawn.", "intermediate"),
        ("Confianza", "Trust / confidence.", "intermediate"),
        ("Sabiduría", "Wisdom.", "advanced"),
    ],
    "ja": [
        ("こんにちは", "Konnichiwa — hello.", "beginner"),
        ("ありがとう", "Arigatou — thank you.", "beginner"),
        ("さくら", "Sakura — cherry blossom.", "beginner"),
        ("友達", "Tomodachi — friend.", "beginner"),
        ("学ぶ", "Manabu — to learn.", "beginner"),
        ("大切", "Taisetsu — important, precious.", "intermediate"),
        ("勇気", "Yuuki — courage.", "intermediate"),
        ("努力", "Doryoku — effort.", "intermediate"),
    ],
    "ko": [
        ("안녕하세요", "Annyeonghaseyo — hello.", "beginner"),
        ("감사합니다", "Gamsahamnida — thank you.", "beginner"),
        ("친구", "Chingu — friend.", "beginner"),
        ("사랑", "Sarang — love.", "beginner"),
        ("행복", "Haengbok — happiness.", "beginner"),
        ("공부", "Gongbu — study.", "beginner"),
    ],
    "fr": [
        ("Bonjour", "Hello / good day.", "beginner"),
        ("Merci", "Thank you.", "beginner"),
        ("Amitié", "Friendship.", "beginner"),
        ("Découvrir", "To discover.", "intermediate"),
        ("Aventure", "Adventure.", "beginner"),
        ("Bienveillance", "Kindness / benevolence.", "advanced"),
    ],
    "de": [
        ("Hallo", "Hello.", "beginner"),
        ("Danke", "Thank you.", "beginner"),
        ("Freundschaft", "Friendship.", "beginner"),
        ("Abenteuer", "Adventure.", "beginner"),
        ("Fernweh", "Longing for far-off places.", "advanced"),
    ],
    "zh": [
        ("你好", "Nǐ hǎo — hello.", "beginner"),
        ("谢谢", "Xièxiè — thank you.", "beginner"),
        ("朋友", "Péngyǒu — friend.", "beginner"),
        ("学习", "Xuéxí — to study.", "beginner"),
        ("勇气", "Yǒngqì — courage.", "intermediate"),
    ],
    "pt": [
        ("Olá", "Hello.", "beginner"),
        ("Obrigado", "Thank you (male speaker).", "beginner"),
        ("Amizade", "Friendship.", "beginner"),
        ("Descoberta", "Discovery.", "intermediate"),
        ("Saudade", "Deep longing / nostalgia.", "advanced"),
    ],
}


async def ensure_seed() -> None:
    """Insert curated vocab if a language bucket is empty. Idempotent."""
    for lang, words in SEED_VOCAB.items():
        exists = await vocab_col.count_documents({"language": lang}, limit=1)
        if exists:
            continue
        docs = [
            {
                "_id": str(uuid.uuid4()),
                "language": lang,
                "word": w,
                "meaning": m,
                "level": lv,
                "created_at": datetime.now(timezone.utc).isoformat(),
            }
            for (w, m, lv) in words
        ]
        if docs:
            await vocab_col.insert_many(docs)


# ─── Schedule helpers ────────────────────────────────────────────────────────

def _schedule_next(interval_days: int, grade: str) -> tuple[int, str]:
    """Return (new_interval_days, next_review_iso). SM-2 lite:
    correct → double the interval (min 1); hard → keep; wrong → reset to 0.
    """
    if grade == "correct":
        new_interval = max(1, interval_days * 2 if interval_days > 0 else 1)
    elif grade == "hard":
        new_interval = max(0, interval_days)
    else:  # wrong / anything else
        new_interval = 0
    next_review = datetime.now(timezone.utc) + timedelta(days=new_interval)
    return new_interval, next_review.isoformat()


def _card_public(card: dict, vocab: dict | None) -> dict:
    return {
        "id": card["_id"],
        "vocab_id": card["vocab_id"],
        "word": (vocab or {}).get("word"),
        "meaning": (vocab or {}).get("meaning"),
        "level": (vocab or {}).get("level"),
        "language": (vocab or {}).get("language") or card.get("language"),
        "streak": card.get("streak", 0),
        "interval_days": card.get("interval_days", 0),
        "next_review": card.get("next_review"),
        "last_result": card.get("last_result"),
    }


# ─── Endpoints ───────────────────────────────────────────────────────────────

@router.get("/status")
async def status(current_user: CurrentUser, language: Optional[str] = None):
    """Compact summary for the Learn dashboard: chosen language, how many
    words are due today, mistakes count, total mastered."""
    await ensure_seed()
    lang = language or current_user.get("learning_language") or "en"
    now = datetime.now(timezone.utc).isoformat()
    user_id = current_user["_id"]
    all_cards = await cards_col.find(
        {"user_id": user_id, "language": lang}
    ).to_list(1000)
    due = [c for c in all_cards if not c.get("next_review") or c["next_review"] <= now]
    mistakes = [c for c in all_cards if c.get("last_result") == "wrong"]
    mastered = [c for c in all_cards if c.get("interval_days", 0) >= 8]
    total_vocab = await vocab_col.count_documents({"language": lang})
    seen_ids = {c["vocab_id"] for c in all_cards}
    unseen = max(0, total_vocab - len(seen_ids))
    return {
        "language": lang,
        "due_count": min(20, len(due) + unseen),  # cap the daily set at 20
        "mistakes_count": len(mistakes),
        "mastered_count": len(mastered),
        "total_vocab": total_vocab,
        "streak_days": current_user.get("streak_count", 1),
    }


@router.get("/session")
async def session(current_user: CurrentUser, language: Optional[str] = None):
    """Return the next batch of cards to review — a mix of due existing cards
    and new (unseen) words to keep the session engaging."""
    await ensure_seed()
    lang = language or current_user.get("learning_language") or "en"
    now = datetime.now(timezone.utc).isoformat()
    user_id = current_user["_id"]
    existing = await cards_col.find(
        {"user_id": user_id, "language": lang}
    ).to_list(500)
    seen_ids = {c["vocab_id"] for c in existing}
    due_cards = sorted(
        [c for c in existing if not c.get("next_review") or c["next_review"] <= now],
        key=lambda c: c.get("next_review") or "",
    )
    # Pick some new vocab if we have room.
    slots = max(0, 12 - len(due_cards))
    new_vocab = []
    if slots:
        new_vocab = (
            await vocab_col.find(
                {"language": lang, "_id": {"$nin": list(seen_ids)}}
            )
            .limit(slots)
            .to_list(slots)
        )
    # Compose the batch: prepend new words then queue due cards.
    out = []
    for v in new_vocab:
        out.append(
            {
                "id": None,
                "vocab_id": v["_id"],
                "word": v["word"],
                "meaning": v["meaning"],
                "level": v.get("level"),
                "language": lang,
                "streak": 0,
                "is_new": True,
            }
        )
    if due_cards:
        vocab_ids = [c["vocab_id"] for c in due_cards]
        vocab_docs = await vocab_col.find(
            {"_id": {"$in": vocab_ids}}
        ).to_list(len(vocab_ids))
        by_id = {v["_id"]: v for v in vocab_docs}
        for c in due_cards:
            out.append({**_card_public(c, by_id.get(c["vocab_id"])), "is_new": False})
    return {"language": lang, "cards": out[:20]}


class ReviewBody(BaseModel):
    vocab_id: str
    grade: str = Field(pattern="^(correct|hard|wrong)$")


@router.post("/review")
async def review(body: ReviewBody, current_user: CurrentUser):
    """Record the outcome of one card review. Creates the user's card row on
    first sight of a word."""
    vocab = await vocab_col.find_one({"_id": body.vocab_id})
    if not vocab:
        raise HTTPException(status_code=404, detail="Vocab word not found")
    user_id = current_user["_id"]
    card = await cards_col.find_one(
        {"user_id": user_id, "vocab_id": body.vocab_id}
    )
    prev_interval = (card or {}).get("interval_days", 0)
    prev_streak = (card or {}).get("streak", 0)
    new_streak = prev_streak + 1 if body.grade == "correct" else 0
    new_interval, next_review = _schedule_next(prev_interval, body.grade)
    doc = {
        "user_id": user_id,
        "vocab_id": body.vocab_id,
        "language": vocab["language"],
        "streak": new_streak,
        "interval_days": new_interval,
        "next_review": next_review,
        "last_result": body.grade,
        "updated_at": datetime.now(timezone.utc).isoformat(),
    }
    if card:
        await cards_col.update_one(
            {"_id": card["_id"]}, {"$set": doc}
        )
        doc["_id"] = card["_id"]
    else:
        doc["_id"] = str(uuid.uuid4())
        doc["created_at"] = doc["updated_at"]
        await cards_col.insert_one(doc)
    return _card_public(doc, vocab)


@router.get("/vocabulary")
async def vocabulary(current_user: CurrentUser, language: Optional[str] = None):
    """Full vocab list for a language — used by the 'All Items' tile."""
    await ensure_seed()
    lang = language or current_user.get("learning_language") or "en"
    docs = await vocab_col.find({"language": lang}).to_list(500)
    user_cards = await cards_col.find(
        {"user_id": current_user["_id"], "language": lang}
    ).to_list(500)
    card_by_vid = {c["vocab_id"]: c for c in user_cards}
    return [
        {
            "id": d["_id"],
            "word": d["word"],
            "meaning": d["meaning"],
            "level": d.get("level"),
            "language": d["language"],
            "seen": d["_id"] in card_by_vid,
            "streak": (card_by_vid.get(d["_id"]) or {}).get("streak", 0),
            "last_result": (card_by_vid.get(d["_id"]) or {}).get("last_result"),
        }
        for d in docs
    ]


@router.get("/mistakes")
async def mistakes(current_user: CurrentUser, language: Optional[str] = None):
    """Words the user got wrong in the most recent review — the 'Recent
    Mistakes' tile."""
    lang = language or current_user.get("learning_language") or "en"
    cards = await cards_col.find(
        {"user_id": current_user["_id"], "language": lang, "last_result": "wrong"}
    ).to_list(200)
    if not cards:
        return []
    vocab_docs = await vocab_col.find(
        {"_id": {"$in": [c["vocab_id"] for c in cards]}}
    ).to_list(len(cards))
    by_id = {v["_id"]: v for v in vocab_docs}
    return [_card_public(c, by_id.get(c["vocab_id"])) for c in cards]


class CollectionCreate(BaseModel):
    name: str = Field(min_length=1, max_length=60)
    language: Optional[str] = None
    vocab_ids: list[str] = Field(default_factory=list, max_length=200)


@router.get("/collections")
async def list_collections(current_user: CurrentUser):
    docs = await collections_col.find(
        {"user_id": current_user["_id"]}
    ).sort("created_at", -1).to_list(100)
    return [
        {
            "id": d["_id"],
            "name": d["name"],
            "language": d.get("language"),
            "count": len(d.get("vocab_ids") or []),
            "created_at": d.get("created_at"),
        }
        for d in docs
    ]


@router.post("/collections", status_code=201)
async def create_collection(body: CollectionCreate, current_user: CurrentUser):
    doc = {
        "_id": str(uuid.uuid4()),
        "user_id": current_user["_id"],
        "name": body.name.strip(),
        "language": body.language,
        "vocab_ids": body.vocab_ids,
        "created_at": datetime.now(timezone.utc).isoformat(),
    }
    await collections_col.insert_one(doc)
    return {
        "id": doc["_id"],
        "name": doc["name"],
        "language": doc["language"],
        "count": len(doc["vocab_ids"]),
        "created_at": doc["created_at"],
    }
