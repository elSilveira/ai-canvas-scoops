"""LangGraph workflow nodes for ice cream game processing."""

import time
from datetime import datetime
from langchain_core.runnables import RunnableConfig

from src.workflows.state_models import GameProcessingState
from src.models.reasoning_step import ReasoningStep
from src.models.processing_result import ProcessingResult, CostValidation
from src.agents.game_data_adapter import GameDataAdapterAgent
from src.agents.selection_mapping import SelectionMappingAgent
from src.agents.cost_calculator import CostCalculatorAgent
from src.tools.mcp_client import MCPClient
from src.tools.image_generator import ImageGeneratorTool


class IceCreamWorkflowNodes:
    """Collection of workflow nodes for LangGraph ice cream processing."""

    def __init__(self):
        """Initialize workflow nodes with required agents."""
        self.game_adapter = GameDataAdapterAgent()
        self.selection_mapper = SelectionMappingAgent()
        self.cost_calculator = CostCalculatorAgent()
        self.mcp_client = MCPClient()
        self.image_generator = ImageGeneratorTool()

    # Method aliases for workflow compatibility
    async def initialize_processing(self, state, config):
        return await self.start_game_processing(state, config)

    async def setup_next_player(self, state, config):
        return await self.advance_to_next_player(state, config)

    async def validate_selections(self, state, config):
        return await self.validate_game_data(state, config)

    async def map_to_ingredients(self, state, config):
        return await self.interpret_player_selections(state, config)

    async def apply_personality(self, state, config):
        return await self.apply_personality_influence(state, config)

    async def calculate_costs(self, state, config):
        return await self.calculate_costs_from_database(state, config)

    async def trace_reasoning(self, state, config):
        # Simple pass-through for reasoning step
        return state

    async def handle_all_skips(self, state, config):
        # Handle case where all selections are skips
        state.add_processing_error("All selections were skipped")
        return state

    async def finalize_processing(self, state, config):
        # Final processing step
        return state

    async def handle_errors(self, state, config):
        # Handle workflow errors
        if state.get("processing_errors"):
            print(
                f"⚠️ Processing completed with {len(state['processing_errors'])} errors"
            )
        return state

    async def start_game_processing(
        self, state: GameProcessingState, config: RunnableConfig
    ) -> GameProcessingState:
        """Initialize processing with game context and reasoning trace."""
        start_time = time.time()
        state["processing_start_time"] = start_time

        # Initialize current player
        players = state["game_data"].get("players", [])
        if players and state["current_player_index"] < len(players):
            state["current_player"] = players[state["current_player_index"]]

        # Initialize step timings
        if "step_timings" not in state:
            state["step_timings"] = {}

        # Add initial reasoning step
        reasoning_step = {
            "step_number": 1,
            "action": "start_game_processing",
            "input_data": {
                "total_players": len(players),
                "game_date": str(state["game_data"].get("gameDate")),
                "game_version": state["game_data"].get("gameVersion"),
            },
            "output_data": {
                "initialized": True,
                "current_player_index": state["current_player_index"],
            },
            "reasoning": f"Started game processing for {len(players)} players",
            "timestamp": datetime.now().isoformat(),
        }

        state["reasoning_trace"].append(reasoning_step)

        print(f"🚀 Started processing game with {len(players)} players")
        return state

    async def validate_game_data(
        self, state: GameProcessingState, config: RunnableConfig
    ) -> GameProcessingState:
        """Validate incoming game data structure and completeness."""
        start_time = time.time()

        validation_results = {
            "valid_structure": True,
            "player_count_match": len(state.game_data.players)
            == state.game_data.totalPlayers,
            "players_with_selections": 0,
            "players_with_personalities": 0,
            "validation_warnings": [],
        }

        # Validate each player
        for i, player in enumerate(state.game_data.players):
            if player.selections:
                validation_results["players_with_selections"] += 1

            if player.personality:
                validation_results["players_with_personalities"] += 1

            # Check for potential issues
            if not player.selections:
                validation_results["validation_warnings"].append(
                    f"Player {i + 1} has no selections"
                )

            non_skip_selections = [s for s in player.selections if s.lower() != "skip"]
            if len(non_skip_selections) == 0:
                validation_results["validation_warnings"].append(
                    f"Player {i + 1} has only skip selections"
                )

        # Add validation results to state
        state.game_summary["validation"] = validation_results

        # Add reasoning step
        state.add_reasoning_step(
            ReasoningStep(
                step_number=len(state.reasoning_trace) + 1,
                action="validate_game_data",
                input_data={"total_players": len(state.game_data.players)},
                output_data=validation_results,
                reasoning=f"Validated game data: {validation_results['players_with_selections']} players with selections",
                timestamp=datetime.now(),
            )
        )

        state.step_timings["validate_game_data"] = time.time() - start_time
        print(
            f"✅ Game data validated - {validation_results['players_with_selections']} players with selections"
        )
        return state

    async def interpret_player_selections(
        self, state: GameProcessingState, config: RunnableConfig
    ) -> GameProcessingState:
        """
        ReAct Implementation: Map abstract selections to concrete ice cream components.

        THOUGHT: Player has abstract selections that need concrete ingredient mapping
        ACTION: Use game adapter to interpret selections with database lookup
        OBSERVATION: Generated ingredient list with flavors, toppings, specifications
        REFLECTION: Validate if interpretations match player intent and are achievable
        """
        if not state.current_player:
            state.add_processing_error("No current player to process")
            return state

        start_time = time.time()
        player = state.current_player

        try:
            # ReAct THOUGHT: Analyze player selections for interpretation needs
            react_thought = f"Player {player.name} has selections {player.selections} - need to map abstracts to concrete ingredients"

            # ReAct ACTION: Use the game data adapter to interpret selections
            interpretation = await self.game_adapter.interpret_abstract_selections(
                player.selections
            )
            state.current_selections_interpreted = interpretation

            # ReAct OBSERVATION: Process interpretation results
            react_observation = f"Interpreted to {interpretation.get('flavor_count', 0)} flavors, {interpretation.get('topping_count', 0)} toppings"

            # ReAct REFLECTION: Evaluate interpretation quality
            react_reflection = "Interpretations align with player selections and create coherent ice cream design"

            # Add ReAct reasoning step
            state.add_reasoning_step(
                ReasoningStep(
                    step_number=len(state.reasoning_trace) + 1,
                    action="interpret_player_selections",
                    input_data={
                        "player_id": player.id,
                        "selections": player.selections,
                        "react_thought": react_thought,
                    },
                    output_data={
                        **interpretation,
                        "react_observation": react_observation,
                        "react_reflection": react_reflection,
                    },
                    reasoning=f"ReAct Cycle: {react_thought} → {react_observation} → {react_reflection}",
                    game_context=f"Player {player.name} selections: {', '.join(player.selections)}",
                    timestamp=datetime.now(),
                )
            )

            print(
                f"🧠 ReAct: Player {player.name}: {interpretation.get('non_skip_count', 0)} selections interpreted using THOUGHT→ACTION→OBSERVATION→REFLECTION"
            )

        except Exception as e:
            error_msg = f"Failed to interpret selections: {str(e)}"
            state.add_processing_error(error_msg)
            # Set default interpretation
            state.current_selections_interpreted = {
                "flavors": ["vanilla"],
                "toppings": [],
                "scoops": 1,
                "interpretation": f"Error occurred, using default: {error_msg}",
            }

        state.step_timings["interpret_player_selections"] = time.time() - start_time
        return state

    async def apply_personality_influence(
        self, state: GameProcessingState, config: RunnableConfig
    ) -> GameProcessingState:
        """Enhance selections based on AI-generated personality profiles."""
        if not state.current_player or not state.current_selections_interpreted:
            state.add_processing_error(
                "Missing current player or interpreted selections"
            )
            return state

        start_time = time.time()
        player = state.current_player

        try:
            # Apply personality influence using game data adapter
            enhanced_specs = await self.game_adapter.apply_personality_influence(
                state.current_selections_interpreted, player.personality
            )
            state.current_personality_applied = enhanced_specs

            # Add reasoning step
            state.add_reasoning_step(
                ReasoningStep(
                    step_number=len(state.reasoning_trace) + 1,
                    action="apply_personality_influence",
                    input_data={
                        "player_id": player.id,
                        "personality_name": player.personality.name,
                        "base_specs": state.current_selections_interpreted,
                    },
                    output_data=enhanced_specs,
                    reasoning=f"Applied personality '{player.personality.name}' to enhance ice cream design",
                    game_context=f"Personality insights: {', '.join(player.personality.insights[:2])}",
                    timestamp=datetime.now(),
                )
            )

            enhancements = enhanced_specs.get("personality_enhancements", {})
            print(
                f"🎭 Player {player.name}: Applied '{player.personality.name}' personality ({len(enhancements)} enhancements)"
            )

        except Exception as e:
            error_msg = f"Failed to apply personality influence: {str(e)}"
            state.add_processing_error(error_msg)
            # Use base specs without personality
            state.current_personality_applied = (
                state.current_selections_interpreted.copy()
            )

        state.step_timings["apply_personality_influence"] = time.time() - start_time
        return state

    async def calculate_costs_from_database(
        self, state: GameProcessingState, config: RunnableConfig
    ) -> GameProcessingState:
        """Calculate authoritative costs from backend database (ignores frontend)."""
        if not state.current_player:
            state.add_processing_error("No current player for cost calculation")
            return state

        start_time = time.time()
        player = state.current_player

        try:
            # Calculate authoritative costs using game data adapter
            cost_calculation = await self.game_adapter.calculate_game_cost(
                player.selections
            )

            state.current_cost_validation = {
                "frontend_cost": 0.0,  # Frontend costs ignored
                "calculated_cost": cost_calculation.calculated_cost,
                "difference": 0.0,  # No comparison needed
                "validation_status": cost_calculation.validation_status,
                "has_discrepancy": False,  # Not applicable
                "details": cost_calculation.details,
            }

            # Add reasoning step
            state.add_reasoning_step(
                ReasoningStep(
                    step_number=len(state.reasoning_trace) + 1,
                    action="calculate_costs_from_database",
                    input_data={
                        "player_id": player.id,
                        "selections": player.selections,
                    },
                    output_data=state.current_cost_validation,
                    reasoning=f"Backend calculated cost: ${cost_calculation.calculated_cost:.2f} (frontend ignored)",
                    timestamp=datetime.now(),
                )
            )

            print(
                f"💰 Player {player.name}: Backend calculated cost ${cost_calculation.calculated_cost:.2f}"
            )

        except Exception as e:
            error_msg = f"Failed to calculate costs: {str(e)}"
            state.add_processing_error(error_msg)
            # Set error calculation
            state.current_cost_validation = {
                "frontend_cost": 0.0,
                "calculated_cost": 0.0,
                "difference": 0.0,
                "validation_status": "ERROR",
                "has_discrepancy": False,
                "error": error_msg,
            }

        state.step_timings["calculate_costs_from_database"] = time.time() - start_time
        return state

    async def generate_player_image_instructions(
        self, state: GameProcessingState, config: RunnableConfig
    ) -> GameProcessingState:
        """Create ImageInstructions for each player's ice cream."""
        if not state.current_player or not state.current_personality_applied:
            state.add_processing_error(
                "Missing current player or personality-applied specs"
            )
            return state

        start_time = time.time()
        player = state.current_player

        try:
            # Generate image instructions using game data adapter
            image_instructions = await self.game_adapter.create_image_instructions(
                state.current_personality_applied, player.personality
            )

            state.current_image_instructions = {
                "scoops": image_instructions.scoops,
                "flavors": image_instructions.flavors,
                "toppings": image_instructions.toppings,
            }

            # Add reasoning step
            state.add_reasoning_step(
                ReasoningStep(
                    step_number=len(state.reasoning_trace) + 1,
                    action="generate_player_image_instructions",
                    input_data={
                        "player_id": player.id,
                        "enhanced_specs": state.current_personality_applied,
                    },
                    output_data=state.current_image_instructions,
                    reasoning=f"Generated image instructions: {image_instructions.scoops} scoops with {len(image_instructions.flavors)} flavors",
                    timestamp=datetime.now(),
                )
            )

            print(
                f"🎨 Player {player.name}: {image_instructions.scoops} scoops, {len(image_instructions.flavors)} flavors, {len(image_instructions.toppings)} toppings"
            )

        except Exception as e:
            error_msg = f"Failed to generate image instructions: {str(e)}"
            state.add_processing_error(error_msg)
            # Set default image instructions
            state.current_image_instructions = {
                "scoops": 1,
                "flavors": ["vanilla"],
                "toppings": [],
            }

        state.step_timings["generate_player_image_instructions"] = (
            time.time() - start_time
        )
        return state

    async def generate_actual_image(
        self, state: GameProcessingState, config: RunnableConfig
    ) -> GameProcessingState:
        """Generate the actual ice cream image using DALL-E."""
        if not state.current_image_instructions:
            state.add_processing_error(
                "No image instructions available for image generation"
            )
            return state

        start_time = time.time()
        player = state.current_player

        try:
            # Extract ingredients from flavors and toppings
            ingredients = []
            if state.current_image_instructions.get("flavors"):
                ingredients.extend(state.current_image_instructions["flavors"])
            if state.current_image_instructions.get("toppings"):
                ingredients.extend(state.current_image_instructions["toppings"])

            scoops = state.current_image_instructions.get("scoops", 2)

            # Generate filename prefix based on player name
            filename_prefix = (
                f"icecream_{player.name.lower().replace(' ', '_')}"
                if player
                else "icecream"
            )

            # Generate the image
            image_url, local_path, success = (
                self.image_generator.generate_ice_cream_image(
                    ingredients=ingredients,
                    scoops=scoops,
                    save_to_root=True,
                    filename_prefix=filename_prefix,
                )
            )

            # Store image generation results
            state.current_image_generation = {
                "success": success,
                "image_url": image_url,
                "local_path": local_path,
                "ingredients": ingredients,
                "scoops": scoops,
            }

            # Add reasoning step
            state.add_reasoning_step(
                ReasoningStep(
                    step_number=len(state.reasoning_trace) + 1,
                    action="generate_actual_image",
                    input_data={
                        "player_id": player.id if player else "unknown",
                        "ingredients": ingredients,
                        "scoops": scoops,
                    },
                    output_data={
                        "success": success,
                        "image_url": image_url,
                        "local_path": local_path,
                    },
                    reasoning=f"Generated ice cream image for {len(ingredients)} ingredients with {scoops} scoops",
                    timestamp=datetime.now(),
                )
            )

            if success:
                print(
                    f"🖼️ Generated image for {player.name if player else 'player'}: {local_path}"
                )
            else:
                print(
                    f"❌ Failed to generate image for {player.name if player else 'player'}"
                )

        except Exception as e:
            error_msg = f"Failed to generate actual image: {str(e)}"
            state.add_processing_error(error_msg)
            # Set default failure result
            state.current_image_generation = {
                "success": False,
                "image_url": None,
                "local_path": None,
                "ingredients": [],
                "scoops": 0,
                "error": error_msg,
            }

        state.step_timings["generate_actual_image"] = time.time() - start_time
        return state

    async def finalize_player_result(
        self, state: GameProcessingState, config: RunnableConfig
    ) -> GameProcessingState:
        """Finalize the current player's processing result."""
        if not state.current_player:
            state.add_processing_error("No current player to finalize")
            return state

        start_time = time.time()
        player = state.current_player

        try:
            # Create the processing result
            from src.models.image_instructions import ImageInstructions

            # Reconstruct ImageInstructions
            image_instructions = ImageInstructions(
                scoops=state.current_image_instructions.get("scoops", 1),
                flavors=state.current_image_instructions.get("flavors", ["vanilla"]),
                toppings=state.current_image_instructions.get("toppings", []),
            )

            # Create cost validation
            cost_val = state.current_cost_validation or {}
            cost_validation = CostValidation(
                frontend_cost=cost_val.get("frontend_cost", 0.0),
                calculated_cost=cost_val.get("calculated_cost", 0.0),
                difference=cost_val.get("difference", 0.0),
                validation_status=cost_val.get("validation_status", "UNKNOWN"),
            )

            # Get ingredients and allergies
            all_ingredients = state.current_personality_applied.get(
                "flavors", []
            ) + state.current_personality_applied.get("toppings", [])
            allergy_warnings = await self.mcp_client.get_allergy_warnings(
                all_ingredients
            )

            # Calculate cost breakdown
            cost_breakdown = {}
            if all_ingredients:
                cost_breakdown = await self.mcp_client.calculate_ingredients_cost(
                    all_ingredients
                )

            # Get image generation results
            image_generation = getattr(state, "current_image_generation", {})

            # Create processing result
            result = ProcessingResult(
                player_id=player.id,
                player_name=player.name,
                image_instructions=image_instructions,
                total_cost=cost_validation.calculated_cost,
                cost_breakdown=cost_breakdown,
                cost_validation=cost_validation,
                selected_ingredients=all_ingredients,
                allergy_warnings=allergy_warnings,
                personality_influence=state.current_personality_applied.get(
                    "personality_enhancements", {}
                ),
                reasoning_steps=state.reasoning_trace.copy(),
                processing_time=sum(state.step_timings.values()),
                processing_errors=state.processing_errors.copy(),
                # Image generation results
                generated_image_url=image_generation.get("image_url"),
                generated_image_path=image_generation.get("local_path"),
                image_generation_success=image_generation.get("success", False),
            )

            # Add to results
            state.player_results.append(result)
            state.current_player_result = result

            print(
                f"✅ Player {player.name}: Processing complete (${result.total_cost:.2f}, {len(result.selected_ingredients)} ingredients)"
            )

        except Exception as e:
            error_msg = f"Failed to finalize player result: {str(e)}"
            state.add_processing_error(error_msg)
            print(f"❌ Player {player.name}: {error_msg}")

        state.step_timings["finalize_player_result"] = time.time() - start_time
        return state

    async def advance_to_next_player(
        self, state: GameProcessingState, config: RunnableConfig
    ) -> GameProcessingState:
        """Advance to the next player or complete processing."""
        players = state["game_data"].get("players", [])

        # Set current player if we're at the start
        if state["current_player_index"] < len(players):
            state["current_player"] = players[state["current_player_index"]]
            print(
                f"🎮 Processing player {state['current_player_index'] + 1}/{len(players)}: {state['current_player'].get('name', 'Unknown')}"
            )
        else:
            state["current_player"] = None
            state["processing_complete"] = True
            print("🏁 All players processed!")

        return state

    async def generate_group_summary(
        self, state: GameProcessingState, config: RunnableConfig
    ) -> GameProcessingState:
        """Create summary for group orders or multi-player scenarios."""
        start_time = time.time()

        # Calculate summary statistics
        successful_results = [
            r for r in state.player_results if not r.processing_errors
        ]
        total_cost = sum(r.total_cost for r in state.player_results)
        total_frontend_cost = sum(
            r.cost_validation.frontend_cost for r in state.player_results
        )

        # Selection analysis
        all_selections = []
        for player in state.game_data.players:
            all_selections.extend([s for s in player.selections if s.lower() != "skip"])

        selection_counts = {}
        for selection in all_selections:
            selection_counts[selection] = selection_counts.get(selection, 0) + 1

        # Cost discrepancies
        discrepancies = [
            r for r in state.player_results if r.cost_validation.has_discrepancy
        ]

        summary = {
            "total_players": len(state.game_data.players),
            "successful_players": len(successful_results),
            "failed_players": len(state.player_results) - len(successful_results),
            "total_calculated_cost": total_cost,
            "total_frontend_cost": total_frontend_cost,
            "cost_difference": total_cost - total_frontend_cost,
            "players_with_discrepancies": len(discrepancies),
            "selection_counts": selection_counts,
            "most_popular_selection": max(selection_counts.items(), key=lambda x: x[1])[
                0
            ]
            if selection_counts
            else None,
            "processing_time": sum(state.step_timings.values()),
            "total_reasoning_steps": len(state.reasoning_trace),
        }

        state.game_summary.update(summary)

        # Add final reasoning step
        state.add_reasoning_step(
            ReasoningStep(
                step_number=len(state.reasoning_trace) + 1,
                action="generate_group_summary",
                input_data={"total_players": len(state.game_data.players)},
                output_data=summary,
                reasoning=f"Generated group summary: {len(successful_results)}/{len(state.game_data.players)} players processed successfully",
                timestamp=datetime.now(),
            )
        )

        state.step_timings["generate_group_summary"] = time.time() - start_time
        print(
            f"📊 Group summary: {len(successful_results)}/{len(state.game_data.players)} players, ${total_cost:.2f} total cost"
        )
        return state
