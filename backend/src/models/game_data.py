"""Game-based input models from frontend."""

from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel


class AIInteraction(BaseModel):
    """AI thought process for each selection."""

    selection: str
    aiThought: str
    aiEmoji: str
    aiSteps: List[str]
    round: int
    timestamp: datetime


class PersonalityProfile(BaseModel):
    """Generated personality data."""

    name: str
    emoji: str
    description: str
    color: str
    gradient: str
    insights: List[str]


class PlayerData(BaseModel):
    """Individual player data with selections and AI interactions."""

    id: str
    name: str
    selections: List[str]  # e.g., ["Skip", "Rich", "Skip", "Crunchy"]
    totalCost: float
    aiInteractions: List[AIInteraction]
    personality: PersonalityProfile


class GameData(BaseModel):
    """Complete game data from frontend."""

    gameDate: datetime
    players: List[PlayerData]
    totalPlayers: int
    gameVersion: str

    def get_player_by_id(self, player_id: str) -> Optional[PlayerData]:
        """Get player data by ID."""
        for player in self.players:
            if player.id == player_id:
                return player
        return None

    def get_non_skip_selections(self, player_id: str) -> List[str]:
        """Get all non-skip selections for a player."""
        player = self.get_player_by_id(player_id)
        if not player:
            return []
        return [sel for sel in player.selections if sel.lower() != "skip"]

    def has_valid_selections(self, player_id: str) -> bool:
        """Check if player has at least one non-skip selection."""
        return len(self.get_non_skip_selections(player_id)) > 0
