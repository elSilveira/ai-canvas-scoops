"""Session-based memory storage for maintaining game state between requests."""

import asyncio
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
import uuid
import sys
from .session_models import GameSessionData, PlayerSessionData, SessionMemoryStats


class SessionMemory:
    """In-memory session storage with automatic cleanup and expiration."""

    def __init__(self, session_timeout_hours: int = 24):
        """Initialize session memory with configurable timeout."""
        self._sessions: Dict[str, GameSessionData] = {}
        self._session_timeout = timedelta(hours=session_timeout_hours)
        self._cleanup_task = None
        self._start_cleanup_task()

    def _start_cleanup_task(self):
        """Start background task for cleaning up expired sessions."""

        async def cleanup_loop():
            while True:
                await asyncio.sleep(3600)  # Run cleanup every hour
                await self.cleanup_expired_sessions()

        # Start the cleanup task
        try:
            loop = asyncio.get_event_loop()
            self._cleanup_task = loop.create_task(cleanup_loop())
        except RuntimeError:
            # No event loop running yet, cleanup will be handled manually
            pass

    def create_session(self, players: List[Dict[str, Any]]) -> str:
        """Create a new game session with players."""
        session_id = str(uuid.uuid4())
        now = datetime.now()

        # Convert player data to PlayerSessionData
        session_players = []
        for player_data in players:
            player = PlayerSessionData(
                id=player_data.get("id", str(uuid.uuid4())),
                name=player_data.get("name", "Unknown"),
                selections=player_data.get("selections", []),
                ai_interactions=player_data.get("aiInteractions", []),
                total_cost=player_data.get("totalCost", 0.0),
            )
            session_players.append(player)

        # Create session
        session = GameSessionData(
            session_id=session_id,
            created_at=now,
            updated_at=now,
            players=session_players,
            expires_at=now + self._session_timeout,
        )

        self._sessions[session_id] = session
        print(f"✅ Created session {session_id} with {len(session_players)} players")
        return session_id

    def get_session(self, session_id: str) -> Optional[GameSessionData]:
        """Get session data by ID."""
        session = self._sessions.get(session_id)
        if session and session.expires_at > datetime.now():
            return session
        elif session:
            # Session expired, remove it
            del self._sessions[session_id]
            print(f"🗑️ Removed expired session {session_id}")
        return None

    def update_session(self, session_id: str, session_data: GameSessionData) -> bool:
        """Update existing session data."""
        if session_id in self._sessions:
            session_data.updated_at = datetime.now()
            self._sessions[session_id] = session_data
            return True
        return False

    def get_player_from_session(
        self, session_id: str, player_name: str
    ) -> Optional[PlayerSessionData]:
        """Get specific player data from session."""
        session = self.get_session(session_id)
        if session:
            for player in session.players:
                if player.name.lower() == player_name.lower():
                    return player
        return None

    def update_player_in_session(
        self, session_id: str, player_name: str, updates: Dict[str, Any]
    ) -> bool:
        """Update specific player data in session."""
        session = self.get_session(session_id)
        if not session:
            return False

        # Find and update player
        for i, player in enumerate(session.players):
            if player.name.lower() == player_name.lower():
                # Update player data
                for key, value in updates.items():
                    if hasattr(player, key):
                        setattr(player, key, value)

                # Update session
                session.updated_at = datetime.now()
                self._sessions[session_id] = session
                print(f"✅ Updated player {player_name} in session {session_id}")
                return True

        return False

    def store_processing_result(
        self, session_id: str, player_name: str, processing_result: Dict[str, Any]
    ) -> bool:
        """Store AI processing result for a player."""
        return self.update_player_in_session(
            session_id, player_name, {"processing_result": processing_result}
        )

    def store_generated_image(
        self, session_id: str, player_name: str, image_url: str
    ) -> bool:
        """Store generated image URL for a player."""
        return self.update_player_in_session(
            session_id, player_name, {"generated_image_url": image_url}
        )

    def mark_session_complete(self, session_id: str) -> bool:
        """Mark session as completed."""
        session = self.get_session(session_id)
        if session:
            session.status = "completed"
            session.updated_at = datetime.now()
            self._sessions[session_id] = session
            return True
        return False

    def delete_session(self, session_id: str) -> bool:
        """Delete a session."""
        if session_id in self._sessions:
            del self._sessions[session_id]
            print(f"🗑️ Deleted session {session_id}")
            return True
        return False

    async def cleanup_expired_sessions(self) -> int:
        """Clean up expired sessions and return count of removed sessions."""
        now = datetime.now()
        expired_sessions = [
            session_id
            for session_id, session in self._sessions.items()
            if session.expires_at <= now
        ]

        for session_id in expired_sessions:
            del self._sessions[session_id]

        if expired_sessions:
            print(f"🧹 Cleaned up {len(expired_sessions)} expired sessions")

        return len(expired_sessions)

    def get_stats(self) -> SessionMemoryStats:
        """Get memory usage statistics."""
        now = datetime.now()
        active_sessions = sum(1 for s in self._sessions.values() if s.expires_at > now)
        expired_sessions = len(self._sessions) - active_sessions
        total_players = sum(len(s.players) for s in self._sessions.values())

        # Rough memory estimation
        memory_usage_mb = sys.getsizeof(self._sessions) / (1024 * 1024)

        return SessionMemoryStats(
            total_sessions=len(self._sessions),
            active_sessions=active_sessions,
            expired_sessions=expired_sessions,
            total_players=total_players,
            memory_usage_mb=round(memory_usage_mb, 2),
        )

    def list_sessions(self) -> List[str]:
        """List all active session IDs."""
        now = datetime.now()
        return [
            session_id
            for session_id, session in self._sessions.items()
            if session.expires_at > now
        ]


# Global session memory instance
session_memory = SessionMemory()
