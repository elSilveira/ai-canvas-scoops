"""Processing result models with game context and validation."""

from typing import Dict, List, Any, Optional
from pydantic import BaseModel, Field
from src.models.image_instructions import ImageInstructions
from src.models.reasoning_step import ReasoningStep


class CostValidation(BaseModel):
    """Comparison between ignored frontend cost vs authoritative backend calculation."""

    frontend_cost: (
        float  # Value from frontend (for reference only, IGNORED in processing)
    )
    calculated_cost: float  # AUTHORITATIVE cost calculated by backend from database
    difference: float  # Difference between frontend and backend (for analysis only)
    validation_status: str = "FRONTEND_IGNORED"  # Always indicates frontend is ignored
    calculation_method: str = "ingredient_database"  # Always from backend database
    details: Optional[str] = None

    @property
    def has_discrepancy(self) -> bool:
        """Check if there's a difference between frontend and backend (for analysis only)."""
        return abs(self.difference) > 0.01  # Allow for small floating point differences

    @property
    def discrepancy_percentage(self) -> float:
        """Calculate difference as percentage of frontend cost (analysis only)."""
        if self.frontend_cost == 0:
            return 0.0
        return abs(self.difference / self.frontend_cost) * 100


class ProcessingResult(BaseModel):
    """Complete result with structured data and authoritative backend-calculated cost."""

    player_id: str
    player_name: str
    image_instructions: ImageInstructions
    total_cost: (
        float  # AUTHORITATIVE cost calculated by backend using ingredient database
    )
    cost_breakdown: Dict[str, float] = Field(
        default_factory=dict
    )  # Detailed breakdown from backend
    cost_validation: (
        CostValidation  # Shows difference between ignored frontend vs backend
    )
    selected_ingredients: List[str] = Field(default_factory=list)
    allergy_warnings: List[str] = Field(default_factory=list)
    personality_influence: Dict[str, str] = Field(default_factory=dict)
    reasoning_steps: List[ReasoningStep] = Field(default_factory=list)
    processing_time: float = 0.0
    processing_errors: List[str] = Field(default_factory=list)

    # Image generation results
    generated_image_url: Optional[str] = None
    generated_image_path: Optional[str] = None
    image_generation_success: bool = False

    def add_reasoning_step(self, step: ReasoningStep) -> None:
        """Add a reasoning step to the trace."""
        step.step_number = len(self.reasoning_steps) + 1
        self.reasoning_steps.append(step)

    def get_debug_report(self) -> str:
        """Generate a comprehensive debug report."""
        report = f"Processing Report for Player {self.player_name} ({self.player_id})\n"
        report += "=" * 60 + "\n\n"

        report += f"Final Cost: ${self.total_cost:.2f}\n"
        report += f"Cost Validation: {self.cost_validation.validation_status}\n"
        if self.cost_validation.has_discrepancy:
            report += f"Cost Discrepancy: ${self.cost_validation.difference:.2f} ({self.cost_validation.discrepancy_percentage:.1f}%)\n"

        report += f"\nSelected Ingredients: {', '.join(self.selected_ingredients)}\n"
        if self.allergy_warnings:
            report += f"Allergy Warnings: {', '.join(self.allergy_warnings)}\n"

        if self.personality_influence:
            report += "\nPersonality Influence:\n"
            for key, value in self.personality_influence.items():
                report += f"  {key}: {value}\n"

        if self.processing_errors:
            report += "\nProcessing Errors:\n"
            for error in self.processing_errors:
                report += f"  - {error}\n"

        report += f"\nProcessing Time: {self.processing_time:.2f} seconds\n"
        report += f"\nReasoning Steps ({len(self.reasoning_steps)}):\n"
        report += "-" * 40 + "\n"

        for step in self.reasoning_steps:
            report += step.to_debug_string() + "\n"

        return report


class GameProcessingResult(BaseModel):
    """Result for processing an entire game with multiple players."""

    game_date: str
    total_players: int
    player_results: List[ProcessingResult] = Field(default_factory=list)
    game_summary: Dict[str, Any] = Field(default_factory=dict)
    processing_errors: List[str] = Field(default_factory=list)
    total_processing_time: float = 0.0

    def add_player_result(self, result: ProcessingResult) -> None:
        """Add a player result to the game processing result."""
        self.player_results.append(result)

    def get_cost_summary(self) -> Dict[str, Any]:
        """Get cost validation summary for all players."""
        total_frontend_cost = sum(
            r.cost_validation.frontend_cost for r in self.player_results
        )
        total_calculated_cost = sum(
            r.cost_validation.calculated_cost for r in self.player_results
        )
        discrepancies = [
            r for r in self.player_results if r.cost_validation.has_discrepancy
        ]

        return {
            "total_frontend_cost": total_frontend_cost,
            "total_calculated_cost": total_calculated_cost,
            "total_difference": total_calculated_cost - total_frontend_cost,
            "players_with_discrepancies": len(discrepancies),
            "largest_discrepancy": max(
                (r.cost_validation.difference for r in discrepancies), default=0.0
            ),
            "average_processing_time": sum(
                r.processing_time for r in self.player_results
            )
            / len(self.player_results)
            if self.player_results
            else 0.0,
        }
