"""Complete LangGraph workflow definition for AI Canvas Scoops."""

from typing import Any, Dict
from langgraph.graph import StateGraph, END

from src.workflows.state_models import GameProcessingState
from src.workflows.workflow_nodes import IceCreamWorkflowNodes
from src.workflows.decision_nodes import IceCreamWorkflowDecisions


class IceCreamLangGraphWorkflow:
    """Complete LangGraph workflow for processing AI Canvas Scoops game data."""

    def __init__(self, checkpointer_path: str = None):
        """Initialize the workflow with optional checkpointing."""
        # Initialize workflow components
        self.nodes = IceCreamWorkflowNodes()
        self.decisions = IceCreamWorkflowDecisions()

        # Initialize checkpointer for workflow persistence
        self.checkpointer = None
        if checkpointer_path:
            # Note: Checkpointing disabled for this simple implementation
            # Can be enabled with: from langgraph.checkpoint.sqlite import SqliteSaver
            # self.checkpointer = SqliteSaver.from_conn_string(checkpointer_path)
            pass

        # Build the workflow graph
        self.workflow = self._build_workflow()

    def _build_workflow(self) -> StateGraph:
        """Build the complete LangGraph workflow with all nodes and edges."""

        # Create the workflow graph with state model
        workflow = StateGraph(GameProcessingState)

        # Add all workflow nodes
        workflow.add_node("initialize_processing", self.nodes.initialize_processing)
        workflow.add_node("setup_next_player", self.nodes.setup_next_player)
        workflow.add_node("validate_selections", self.nodes.validate_selections)
        workflow.add_node("map_to_ingredients", self.nodes.map_to_ingredients)
        workflow.add_node("apply_personality", self.nodes.apply_personality)
        workflow.add_node("calculate_costs", self.nodes.calculate_costs)
        workflow.add_node(
            "generate_image_instructions", self.nodes.generate_player_image_instructions
        )
        workflow.add_node("generate_actual_image", self.nodes.generate_actual_image)
        workflow.add_node("trace_reasoning", self.nodes.trace_reasoning)
        workflow.add_node("finalize_player_result", self.nodes.finalize_player_result)
        workflow.add_node("handle_all_skips", self.nodes.handle_all_skips)
        workflow.add_node("generate_group_summary", self.nodes.generate_group_summary)
        workflow.add_node("finalize_processing", self.nodes.finalize_processing)
        workflow.add_node("handle_errors", self.nodes.handle_errors)

        # Set entry point
        workflow.set_entry_point("initialize_processing")

        # Main workflow edges
        workflow.add_edge("initialize_processing", "setup_next_player")

        # Conditional routing from player setup
        workflow.add_conditional_edges(
            "setup_next_player",
            self.decisions.has_more_players,
            {
                "continue_processing": "validate_selections",
                "complete_processing": "generate_group_summary",
            },
        )

        # Selection validation routing
        workflow.add_conditional_edges(
            "validate_selections",
            self.decisions.has_valid_selections,
            {
                "all_skips": "handle_all_skips",
                "standard_processing": "map_to_ingredients",
                "full_processing": "map_to_ingredients",
                "no_player": "handle_errors",
            },
        )

        # All-skips handling returns to finalize
        workflow.add_edge("handle_all_skips", "finalize_player_result")

        # Main processing chain
        workflow.add_edge("map_to_ingredients", "calculate_costs")

        # Personality enhancement decision
        workflow.add_conditional_edges(
            "calculate_costs",
            self.decisions.needs_personality_enhancement,
            {
                "apply_personality": "apply_personality",
                "skip_personality": "generate_image_instructions",
            },
        )

        # Continue from personality to image generation
        workflow.add_edge("apply_personality", "generate_image_instructions")

        # Complete player processing chain: instructions -> actual image -> reasoning
        workflow.add_edge("generate_image_instructions", "generate_actual_image")
        workflow.add_edge("generate_actual_image", "trace_reasoning")
        workflow.add_edge("trace_reasoning", "finalize_player_result")

        # Loop back for next player
        workflow.add_edge("finalize_player_result", "setup_next_player")

        # Group summary decision
        workflow.add_conditional_edges(
            "generate_group_summary",
            self.decisions.should_generate_group_summary,
            {
                "generate_summary": "finalize_processing",
                "skip_summary": "finalize_processing",
            },
        )

        # Error handling
        workflow.add_edge("handle_errors", "finalize_processing")

        # Final completion
        workflow.add_edge("finalize_processing", END)

        return workflow

    async def process_game_data(
        self, game_data: dict, config: dict = None, thread_id: str = None
    ) -> Dict[str, Any]:
        """
        Main entry point for processing game data through the workflow.

        Args:
            game_data: The game data from frontend
            config: Optional LangGraph config
            thread_id: Optional thread ID for checkpointing

        Returns:
            Complete processing results
        """
        # Initialize state
        initial_state: GameProcessingState = {
            "game_data": game_data,
            "current_player_index": 0,
            "current_player": None,
            "player_results": [],
            "current_player_result": None,
            "group_summary": {},
            "current_cost_validation": {},
            "reasoning_trace": [],
            "processing_errors": [],
            "skip_personality_enhancement": config.get("skip_personality", False)
            if config
            else False,
            "is_group_order": len(game_data.get("players", [])) > 1,
            "workflow_metadata": {},
        }

        # Prepare config
        run_config = {"configurable": {}}
        if thread_id and self.checkpointer:
            run_config["configurable"]["thread_id"] = thread_id
        if config:
            run_config.update(config)

        try:
            # Compile workflow with checkpointing if available
            if self.checkpointer:
                compiled_workflow = self.workflow.compile(
                    checkpointer=self.checkpointer
                )
            else:
                compiled_workflow = self.workflow.compile()

            # Execute workflow
            result = await compiled_workflow.ainvoke(initial_state, config=run_config)

            return {
                "success": True,
                "results": result.get("player_results", []),
                "group_summary": result.get("group_summary"),
                "processing_errors": result.get("processing_errors", []),
                "workflow_metadata": {
                    "total_players": len(result.get("player_results", [])),
                    "has_errors": len(result.get("processing_errors", [])) > 0,
                    "thread_id": thread_id,
                },
            }

        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "processing_errors": [f"Workflow execution failed: {str(e)}"],
                "results": [],
            }

    async def process_single_player(
        self, player_data: dict, config: dict = None
    ) -> Dict[str, Any]:
        """
        Process a single player through the workflow.

        Args:
            player_data: Individual player data
            config: Optional configuration

        Returns:
            Single player processing result
        """
        # Wrap in game data structure
        game_data = {"players": [player_data], "game_metadata": {"single_player": True}}

        return await self.process_game_data(game_data, config)

    def get_workflow_visualization(self) -> str:
        """Get a text representation of the workflow for debugging."""
        return """
AI Canvas Scoops LangGraph Workflow:

START
  ↓
initialize_processing
  ↓
setup_next_player
  ↓ (has_more_players?)
  ├─ continue_processing → validate_selections
  └─ complete_processing → generate_group_summary
      
validate_selections (has_valid_selections?)
  ├─ all_skips → handle_all_skips → finalize_player_result
  ├─ standard_processing → map_to_ingredients
  ├─ full_processing → map_to_ingredients  
  └─ no_player → handle_errors

map_to_ingredients
  ↓
calculate_costs (needs_personality_enhancement?)
  ├─ apply_personality → apply_personality → generate_image_instructions
  └─ skip_personality → generate_image_instructions

generate_image_instructions
  ↓
trace_reasoning
  ↓
finalize_player_result
  ↓ (loop back to setup_next_player)

generate_group_summary (should_generate_group_summary?)
  ├─ generate_summary → finalize_processing
  └─ skip_summary → finalize_processing

handle_errors → finalize_processing
finalize_processing → END
        """

    async def stream_workflow_execution(
        self, game_data: dict, config: dict = None, thread_id: str = None
    ):
        """
        Stream workflow execution for real-time monitoring.

        Args:
            game_data: The game data to process
            config: Optional configuration
            thread_id: Optional thread ID

        Yields:
            Workflow execution updates
        """
        initial_state = GameProcessingState(
            game_data=game_data,
            current_player_index=0,
            player_results=[],
            processing_errors=[],
        )

        run_config = {"configurable": {}}
        if thread_id and self.checkpointer:
            run_config["configurable"]["thread_id"] = thread_id
        if config:
            run_config.update(config)

        try:
            if self.checkpointer:
                compiled_workflow = self.workflow.compile(
                    checkpointer=self.checkpointer
                )
            else:
                compiled_workflow = self.workflow.compile()

            async for chunk in compiled_workflow.astream(
                initial_state.dict(), config=run_config
            ):
                yield {
                    "node": chunk.get("node"),
                    "state_updates": chunk.get("state"),
                    "timestamp": chunk.get("timestamp"),
                }

        except Exception as e:
            yield {"error": str(e), "node": "workflow_error", "timestamp": None}
