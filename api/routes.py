from fastapi import APIRouter, HTTPException
from api.schemas import ChatRequest, ChatResponse, UserProfileResponse, RecommendationRequest
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from agents.conversation_agent import process_user_query
from data.user_db import get_user
from agents.rec_agent import RecommendationAgent

router = APIRouter()
rec_agent = RecommendationAgent()

@router.post("/chat", response_model=ChatResponse)
async def chat_endpoint(req: ChatRequest):
    try:
        reply = process_user_query(req.user_id, req.message)
        return ChatResponse(reply=reply)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/profile/{user_id}", response_model=UserProfileResponse)
async def get_profile(user_id: str):
    user = get_user(user_id)
    if not user:
        return UserProfileResponse(preferences="New User", history="")
    return UserProfileResponse(preferences=user['preferences'], history=user['history'])

from api.schemas import ChatRequest, ChatResponse, UserProfileResponse, RecommendationRequest, UpdateProfileRequest
from data.user_db import get_user, update_user_preferences
# ... skips lines 3-6
@router.put("/profile")
async def update_profile(req: UpdateProfileRequest):
    try:
        user = get_user(req.user_id)
        history = user['history'] if user else ""
        update_user_preferences(req.user_id, req.preferences, history)
        
        # Clear the internal engine cache so the next recommendation is fresh
        rec_agent.engine.recommend.cache_clear()
        
        return {"status": "success", "preferences": req.preferences}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/recommend")
async def recommend_endpoint(req: RecommendationRequest):
    try:
        hint = req.hint
        if not hint:
            user_data = get_user(req.user_id)
            if user_data and user_data["preferences"]:
                # Use their latest known preference as a hint (e.g. last preferred genre or movie)
                # Since preferences is a comma-separated string, we can take the last item
                prefs_list = [p.strip() for p in user_data["preferences"].split(",")]
                hint = prefs_list[-1] if prefs_list else None

        recs = rec_agent.get_recommendations(req.user_id, hint, top_n=15)
        return {"recommendations": recs}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
