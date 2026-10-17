from pydantic import BaseModel
from typing import List, Optional

class ChatRequest(BaseModel):
    user_id: str
    message: str

class ChatResponse(BaseModel):
    reply: str

class UserProfileRequest(BaseModel):
    user_id: str

class UserProfileResponse(BaseModel):
    preferences: str
    history: str

class RecommendationRequest(BaseModel):
    user_id: str
    hint: Optional[str] = None

class UpdateProfileRequest(BaseModel):
    user_id: str
    preferences: str
