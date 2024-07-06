from pydantic import BaseModel, Field
from typing import Optional, List


class ReviewRequest(BaseModel):
    game_id: int
    user_id: str
    review: str
    rating: int
    platform_id: int
    image_blob: Optional[str]


class RegisterRequest(BaseModel):
    name: str
    password: str


class RegisterResponse(BaseModel):
    message: str


class LoginRequest(BaseModel):
    name: str
    password: str


class FetchUserReviewsQuery(BaseModel):
    name: str


class GameResponse(BaseModel):
    game_id: int
    name: str


class PlatformResponse(BaseModel):
    platform_id: int
    name: str
