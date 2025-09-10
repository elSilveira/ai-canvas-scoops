"""Decision nodes for LangGraph workflow routing."""

from src.workflows.state_models import GameProcessingState


class IceCreamWorkflowDecisions:
    """Decision nodes for routing workflow execution."""

    @staticmethod
    def has_valid_selections(state: GameProcessingState) -> str:
        """Check if current player has enough non-skip selections for ice cream."""
        current_player = state.get("current_player")
        if not current_player:
            return "no_player"

        non_skip_selections = [
            s for s in current_player.get("selections", []) if s.lower() != "skip"
        ]

        if len(non_skip_selections) == 0:
            return "all_skips"
        elif len(non_skip_selections) >= 2:
            return "full_processing"
        else:
            return "standard_processing"

    @staticmethod
    def needs_personality_enhancement(state: GameProcessingState) -> str:
        """Determine if personality data should influence selections."""
        current_player = state.get("current_player")
        if not current_player or not current_player.get("personality"):
            return "skip_personality"

        # Check if personality has meaningful content
        personality = current_player.get("personality")

        # Handle simple string personalities
        if isinstance(personality, str):
            if personality.lower() in ["empty", "none", "basic"]:
                return "skip_personality"
        else:
            # Handle complex personality objects
            if (
                "empty" in personality.get("name", "").lower()
                or len(personality.get("insights", [])) == 0
            ):
                return "skip_personality"

        # Skip if user requested to skip personality enhancement
        if state.get("skip_personality_enhancement", False):
            return "skip_personality"

        return "apply_personality"

    @staticmethod
    def has_more_players(state: GameProcessingState) -> str:
        """Check if there are more players to process."""
        current_index = state.get("current_player_index", 0)
        total_players = len(state.get("game_data", {}).get("players", []))

        if current_index < total_players:
            return "continue_processing"
        else:
            return "complete_processing"

    @staticmethod
    def should_generate_group_summary(state: GameProcessingState) -> str:
        """Determine if group summary should be generated."""
        if len(state.get("player_results", [])) > 1 or state.get(
            "is_group_order", False
        ):
            return "generate_summary"
        else:
            return "skip_summary"

    @staticmethod
    def has_processing_errors(state: GameProcessingState) -> str:
        """Check if there are processing errors that need handling."""
        if len(state.get("processing_errors", [])) > 0:
            return "handle_errors"
        else:
            return "continue_normal"

    @staticmethod
    def cost_validation_status(state: GameProcessingState) -> str:
        """Route based on cost validation results."""
        if not state.current_cost_validation:
            return "validation_failed"

        status = state.current_cost_validation.get("validation_status", "UNKNOWN")

        if status == "MATCH":
            return "cost_match"
        elif "MINOR" in status:
            return "minor_discrepancy"
        elif "MAJOR" in status:
            return "major_discrepancy"
        else:
            return "validation_error"

    @staticmethod
    def complexity_level(state: GameProcessingState) -> str:
        """Determine processing complexity based on selections."""
        if not state.current_player:
            return "simple"

        non_skip_selections = [
            s for s in state.current_player.selections if s.lower() != "skip"
        ]
        unique_selections = set(non_skip_selections)

        if len(unique_selections) == 0:
            return "minimal"  # All skips
        elif len(unique_selections) == 1:
            return "simple"  # Single selection type
        elif len(unique_selections) == 2:
            return "moderate"  # Two selection types
        else:
            return "complex"  # Multiple different selections

    @staticmethod
    def requires_special_handling(state: GameProcessingState) -> str:
        """Check if player requires special handling."""
        if not state.current_player:
            return "normal"

        player = state.current_player

        # Check for all-skip players
        non_skip = [s for s in player.selections if s.lower() != "skip"]
        if len(non_skip) == 0:
            return "all_skips"

        # Check for high-cost discrepancy
        if (
            state.current_cost_validation
            and state.current_cost_validation.get("has_discrepancy", False)
            and abs(state.current_cost_validation.get("difference", 0)) > 10
        ):
            return "high_cost_discrepancy"

        # Check for personality conflicts
        personality_name = player.personality.name.lower()
        if "empty" in personality_name and len(non_skip) > 0:
            return "personality_selection_conflict"

        return "normal"

    @staticmethod
    def batch_processing_decision(state: GameProcessingState) -> str:
        """Decide on batch vs individual processing approach."""
        # For now, always use individual processing
        # This could be enhanced for batch processing optimization
        return "individual_processing"

    @staticmethod
    def quality_check_decision(state: GameProcessingState) -> str:
        """Quality check routing for final results."""
        if not state.current_player_result:
            return "quality_fail"

        result = state.current_player_result

        # Check for critical issues
        if len(result.processing_errors) > 0:
            return "has_errors"

        # Check for reasonable cost
        if result.total_cost < 0.5 or result.total_cost > 50:
            return "cost_unreasonable"

        # Check for minimal requirements
        if (
            len(result.selected_ingredients) == 0
            and result.image_instructions.scoops == 0
        ):
            return "insufficient_content"

        return "quality_pass"
