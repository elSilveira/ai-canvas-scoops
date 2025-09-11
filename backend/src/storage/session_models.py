"""Session models for storing game state between requests."""

from typing import Dict, List, Any, Optional
from pydantic import BaseModel
from datetime import datetime


class PlayerSessionData(BaseModel):
    """Data stored for a single player during a game session."""

    id: str
    name: str
    selections: List[str]
    ai_interactions: List[Dict[str, Any]] = []
    total_cost: float = 0.0
    processing_result: Optional[Dict[str, Any]] = None
    generated_image_url: Optional[str] = None
    personality: Optional[Dict[str, Any]] = None


class GameSessionData(BaseModel):
    """Complete game session data."""

    session_id: str
    created_at: datetime
    updated_at: datetime
    players: List[PlayerSessionData]
    game_metadata: Dict[str, Any] = {}
    status: str = "active"  # active, completed, expired
    expires_at: datetime


class SessionMemoryStats(BaseModel):
    """Statistics about session memory usage."""

    total_sessions: int
    active_sessions: int
    expired_sessions: int
    total_players: int
    memory_usage_mb: float
