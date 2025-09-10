"""State models for LangGraph workflows."""

from typing import List, Dict, Any, Optional, TypedDict
from pydantic import BaseModel, Field
from src.models.game_data import GameData, PlayerData
from src.models.processing_result import ProcessingResult
from src.models.reasoning_step import ReasoningStep


class GameProcessingState(TypedDict):
    """Enhanced state object for game-based workflow (LangGraph compatible)."""

    # Input data
    game_data: Dict[str, Any]

    # Processing state
    current_player_index: int
    current_player: Optional[Dict[str, Any]]

    # Results
    player_results: List[Dict[str, Any]]
    current_player_result: Optional[Dict[str, Any]]

    # Game-level analysis
    group_summary: Dict[str, Any]
    current_cost_validation: Dict[str, Any]

    # Reasoning and debugging
    reasoning_trace: List[Dict[str, Any]]
    processing_errors: List[str]

    # Processing control
    skip_personality_enhancement: bool
    is_group_order: bool

    # Workflow metadata
    workflow_metadata: Dict[str, Any]


class GameProcessingStatePydantic(BaseModel):
    """Pydantic version for validation and conversion."""

    # Input data
    game_data: GameData

    # Processing state
    current_player_index: int = 0
    current_player: Optional[PlayerData] = None

    # Results
    player_results: List[ProcessingResult] = Field(default_factory=list)
    current_player_result: Optional[ProcessingResult] = None

    # Game-level analysis
    group_summary: Dict[str, Any] = Field(default_factory=dict)
    current_cost_validation: Dict[str, Any] = Field(default_factory=dict)

    # Reasoning and debugging
    reasoning_trace: List[ReasoningStep] = Field(default_factory=list)
    processing_errors: List[str] = Field(default_factory=list)

    # Processing control
    skip_personality_enhancement: bool = False
    is_group_order: bool = False

    # Workflow metadata
    workflow_metadata: Dict[str, Any] = Field(default_factory=dict)

    def has_more_players(self) -> bool:
        """Check if there are more players to process."""
        return self.current_player_index < len(self.game_data.players)

    def get_next_player(self) -> Optional[PlayerData]:
        """Get the next player to process."""
        if self.has_more_players():
            return self.game_data.players[self.current_player_index]
        return None

    def advance_to_next_player(self):
        """Move to the next player in the sequence."""
        self.current_player_index += 1
        self.current_player = self.get_next_player()
        self.current_player_result = None

    def to_typed_dict(self) -> GameProcessingState:
        """Convert to TypedDict for LangGraph."""
        return {
            "game_data": self.game_data.dict(),
            "current_player_index": self.current_player_index,
            "current_player": self.current_player.dict()
            if self.current_player
            else None,
            "player_results": [r.dict() for r in self.player_results],
            "current_player_result": self.current_player_result.dict()
            if self.current_player_result
            else None,
            "group_summary": self.group_summary,
            "current_cost_validation": self.current_cost_validation,
            "reasoning_trace": [step.dict() for step in self.reasoning_trace],
            "processing_errors": self.processing_errors,
            "skip_personality_enhancement": self.skip_personality_enhancement,
            "is_group_order": self.is_group_order,
            "workflow_metadata": self.workflow_metadata,
        }

    @classmethod
    def from_typed_dict(
        cls, state: GameProcessingState
    ) -> "GameProcessingStatePydantic":
        """Create from TypedDict."""
        game_data = GameData(**state["game_data"])

        # Convert current player
        current_player = None
        if state["current_player"]:
            current_player = PlayerData(**state["current_player"])

        # Convert results
        player_results = []
        for result_dict in state["player_results"]:
            player_results.append(ProcessingResult(**result_dict))

        current_player_result = None
        if state["current_player_result"]:
            current_player_result = ProcessingResult(**state["current_player_result"])

        # Convert reasoning trace
        reasoning_trace = []
        for step_dict in state["reasoning_trace"]:
            reasoning_trace.append(ReasoningStep(**step_dict))

        return cls(
            game_data=game_data,
            current_player_index=state["current_player_index"],
            current_player=current_player,
            player_results=player_results,
            current_player_result=current_player_result,
            group_summary=state["group_summary"],
            current_cost_validation=state["current_cost_validation"],
            reasoning_trace=reasoning_trace,
            processing_errors=state["processing_errors"],
            skip_personality_enhancement=state["skip_personality_enhancement"],
            is_group_order=state["is_group_order"],
            workflow_metadata=state["workflow_metadata"],
        )


class PlayerProcessingSubState(BaseModel):
    """Sub-state for individual player processing within the workflow."""

    player_data: PlayerData

    # Processing steps
    selections_interpreted: bool = False
    personality_applied: bool = False
    cost_validated: bool = False
    image_instructions_generated: bool = False

    # Intermediate results
    interpreted_selections: Dict[str, Any] = Field(default_factory=dict)
    personality_enhancements: Dict[str, Any] = Field(default_factory=dict)
    cost_validation_result: Optional[Dict[str, Any]] = None
    final_image_instructions: Optional[Dict[str, Any]] = None

    # Processing metadata
    processing_errors: List[str] = Field(default_factory=list)
    processing_warnings: List[str] = Field(default_factory=list)
    step_timings: Dict[str, float] = Field(default_factory=dict)

    def is_processing_complete(self) -> bool:
        """Check if all processing steps are complete."""
        return (
            self.selections_interpreted
            and self.personality_applied
            and self.cost_validated
            and self.image_instructions_generated
        )

    def has_valid_selections(self) -> bool:
        """Check if player has any non-skip selections."""
        non_skip = [s for s in self.player_data.selections if s.lower() != "skip"]
        return len(non_skip) > 0

    def get_non_skip_selections(self) -> List[str]:
        """Get all non-skip selections."""
        return [s for s in self.player_data.selections if s.lower() != "skip"]
