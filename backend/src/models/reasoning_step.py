"""Reasoning step model for debugging and traceability."""

from datetime import datetime
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class ReasoningStep(BaseModel):
    """Enhanced reasoning step with game context."""

    step_number: int
    action: str  # "interpret_selections", "map_to_flavors", "validate_cost", etc.
    input_data: Dict[str, Any]
    output_data: Dict[str, Any]
    reasoning: str
    game_context: Optional[str] = (
        None  # Reference to game data that influenced decision
    )
    timestamp: datetime = Field(default_factory=datetime.now)
    tool_calls: Optional[List[str]] = None

    def to_debug_string(self) -> str:
        """Generate human-readable debug string."""
        debug_str = f"Step {self.step_number}: {self.action}\n"
        debug_str += f"Timestamp: {self.timestamp}\n"
        debug_str += f"Reasoning: {self.reasoning}\n"
        if self.game_context:
            debug_str += f"Game Context: {self.game_context}\n"
        if self.tool_calls:
            debug_str += f"Tool Calls: {', '.join(self.tool_calls)}\n"
        debug_str += f"Input: {self.input_data}\n"
        debug_str += f"Output: {self.output_data}\n"
        return debug_str
