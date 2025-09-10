"""Simplified LangGraph workflow for Phase 2."""

from typing import Dict, Any
from src.agents.game_data_adapter import GameDataAdapterAgent


class SimpleLangGraphWorkflow:
    """Simplified LangGraph workflow implementation for Phase 2."""

    def __init__(self):
        """Initialize with game data adapter."""
        self.game_adapter = GameDataAdapterAgent()

    async def process_game_data(
        self, game_data: dict, config: dict = None, thread_id: str = None
    ) -> Dict[str, Any]:
        """
        Process game data using a workflow-style approach.

        This is a simplified implementation that demonstrates Phase 2 concepts
        while avoiding complex LangGraph TypedDict compatibility issues.
        """
        print("🎮 Starting simplified LangGraph-style workflow...")

        # Convert raw game data to our models with safe field handling
        from src.models.game_data import GameData, PlayerData, PersonalityProfile

        # Convert players with safe field access
        players = []
        for player_data in game_data.get("players", []):
            # Handle personality data safely
            personality = None
            if "personality" in player_data and player_data["personality"]:
                personality_data = player_data["personality"]
                personality = PersonalityProfile(
                    name=personality_data.get("name", "Unknown"),
                    emoji=personality_data.get("emoji", "😐"),
                    description=personality_data.get("description", ""),
                    color=personality_data.get("color", "#000000"),
                    gradient=personality_data.get("gradient", "#000000"),
                    insights=personality_data.get("insights", []),
                )

            # Create player with safe defaults
            player = PlayerData(
                id=player_data.get("id", f"player_{len(players) + 1}"),
                name=player_data.get("name", "Unknown"),
                selections=player_data.get("selections", []),
                totalCost=player_data.get("totalCost", 0.0),
                aiInteractions=player_data.get("aiInteractions", []),
                personality=personality,
            )
            players.append(player)

        game_data_model = GameData(
            gameDate=game_data.get("gameDate", "2025-01-01T00:00:00.000Z"),
            gameVersion=game_data.get("gameVersion", "1.0"),
            totalPlayers=game_data.get("totalPlayers", len(players)),
            players=players,
        )

        # Process using workflow steps
        workflow_state = await self._execute_workflow_steps(
            game_data_model, config or {}, thread_id
        )

        return {
            "success": True,
            "results": workflow_state["player_results"],
            "group_summary": workflow_state.get("group_summary"),
            "processing_errors": workflow_state.get("processing_errors", []),
            "workflow_metadata": {
                "total_players": len(workflow_state["player_results"]),
                "has_errors": len(workflow_state.get("processing_errors", [])) > 0,
                "thread_id": thread_id,
                "workflow_type": "simplified_langgraph",
            },
        }

    async def _execute_workflow_steps(
        self, game_data, config: dict, thread_id: str
    ) -> Dict[str, Any]:
        """Execute workflow in a step-by-step manner."""

        # Step 1: Initialize workflow state
        print("📋 Step 1: Initialize workflow state")
        state = {
            "game_data": game_data,
            "current_player_index": 0,
            "player_results": [],
            "processing_errors": [],
            "group_summary": {},
            "thread_id": thread_id,
        }

        # Step 2: Process each player in workflow style
        print(f"👥 Step 2: Processing {len(game_data.players)} players")

        for i, player in enumerate(game_data.players):
            print(f"\n🎯 Workflow step for Player {i + 1}: {player.name}")

            # Update state
            state["current_player_index"] = i

            # Process player using sub-workflow
            try:
                player_result = await self._process_player_workflow(
                    player, state, config
                )

                # Convert ProcessingResult to dict for consistency
                player_result_dict = {
                    "player_name": player_result.player_name,
                    "total_cost": player_result.total_cost,
                    "selected_ingredients": player_result.selected_ingredients,
                    "image_instructions": player_result.image_instructions.dict()
                    if hasattr(player_result.image_instructions, "dict")
                    else player_result.image_instructions,
                    "reasoning_steps": [
                        step.dict() if hasattr(step, "dict") else step
                        for step in player_result.reasoning_steps
                    ],
                    "processing_errors": player_result.processing_errors,
                    "cost_validation": player_result.cost_validation.dict()
                    if hasattr(player_result.cost_validation, "dict")
                    else player_result.cost_validation,
                    "personality_enhancement": getattr(
                        player_result, "personality_enhancement", None
                    ),
                }

                state["player_results"].append(player_result_dict)

            except Exception as e:
                error_msg = f"Player {i + 1} processing failed: {str(e)}"
                state["processing_errors"].append(error_msg)
                print(f"❌ {error_msg}")

        # Step 3: Generate group summary if needed
        if len(state["player_results"]) > 1:
            print("\n🎨 Step 3: Generate group summary")
            state["group_summary"] = await self._generate_group_summary_workflow(state)

        print("✅ Workflow execution completed")
        return state

    async def _process_player_workflow(
        self, player, workflow_state: dict, config: dict
    ):
        """Process individual player using workflow sub-steps."""

        # Use the game adapter for actual processing
        # This demonstrates how LangGraph can integrate with existing agents
        result = await self.game_adapter.process_single_player(player)

        # Add workflow metadata
        if hasattr(result, "reasoning_steps") and result.reasoning_steps:
            result.reasoning_steps.append(
                {
                    "action": "workflow_processing",
                    "reasoning": f"Processed via simplified LangGraph workflow (thread: {workflow_state.get('thread_id', 'none')})",
                    "step_number": len(result.reasoning_steps) + 1,
                }
            )

        return result

    async def _generate_group_summary_workflow(self, state: dict) -> Dict[str, Any]:
        """Generate group summary in workflow style."""

        total_cost = sum(r["total_cost"] for r in state["player_results"])
        total_ingredients = sum(
            len(r["selected_ingredients"]) for r in state["player_results"]
        )

        return {
            "workflow_summary": {
                "total_players": len(state["player_results"]),
                "total_cost": total_cost,
                "total_ingredients": total_ingredients,
                "successful_players": len(state["player_results"]),
                "failed_players": len(state["processing_errors"]),
                "workflow_type": "simplified_langgraph",
                "thread_id": state.get("thread_id"),
            }
        }


# Main workflow class for external use
class IceCreamLangGraphWorkflow(SimpleLangGraphWorkflow):
    """Main LangGraph workflow - using simplified implementation for Phase 2."""

    pass
