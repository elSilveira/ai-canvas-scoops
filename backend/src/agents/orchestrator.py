"""Enhanced orchestrator that acts as the main LLM adapter with LangGraph support."""

from datetime import datetime
from typing import List, Dict, Any
from src.models.game_data import GameData, PlayerData
from src.models.processing_result import ProcessingResult, GameProcessingResult
from src.agents.game_data_adapter import GameDataAdapterAgent
from src.agents.selection_mapping import SelectionMappingAgent
from src.agents.cost_calculator import CostCalculatorAgent
from src.agents.reasoning_tracer import ReasoningTracer
from src.tools.mcp_client import MCPClient
from src.workflows.simple_workflow import IceCreamLangGraphWorkflow


class IceCreamGameOrchestrator:
    """
    Main orchestrator that acts as the LLM adapter for game-based ice cream processing.
    Now supports both LangGraph workflow and direct agent processing.
    """

    def __init__(self, use_langgraph: bool = True):
        """Initialize the orchestrator with workflow or direct agent processing."""
        self.use_langgraph = use_langgraph

        # Initialize LangGraph workflow if enabled
        if self.use_langgraph:
            self.workflow = IceCreamLangGraphWorkflow()

        # Initialize direct agents for fallback or non-workflow processing
        self.game_adapter = GameDataAdapterAgent()
        self.selection_mapper = SelectionMappingAgent()
        self.cost_calculator = CostCalculatorAgent()
        self.mcp_client = MCPClient()
        self.reasoning_tracer = ReasoningTracer()

    async def process_game_data(
        self, game_data: GameData, config: Dict[str, Any] = None, thread_id: str = None
    ) -> GameProcessingResult:
        """
        Main entry point - processes complete game data using LangGraph workflow or direct agents.
        """
        if self.use_langgraph:
            return await self._process_with_langgraph(game_data, config, thread_id)
        else:
            return await self._process_with_direct_agents(game_data)

    async def _process_with_langgraph(
        self, game_data: GameData, config: Dict[str, Any] = None, thread_id: str = None
    ) -> GameProcessingResult:
        """Process game data using LangGraph workflow."""
        start_time = datetime.now()
        session_id = thread_id or f"game_{game_data.gameDate.strftime('%Y%m%d_%H%M%S')}"

        try:
            print("🎮 Starting LangGraph workflow processing...")

            # Convert GameData to dict for workflow
            game_data_dict = {
                "players": [
                    {
                        "name": player.name,
                        "selections": player.selections,
                        "personality": {
                            "name": player.personality.name,
                            "insights": player.personality.insights,
                        }
                        if player.personality
                        else None,
                    }
                    for player in game_data.players
                ],
                "gameDate": str(game_data.gameDate),
                "gameVersion": game_data.gameVersion,
                "totalPlayers": game_data.totalPlayers,
            }

            # Execute workflow
            result = await self.workflow.process_game_data(
                game_data=game_data_dict, config=config or {}, thread_id=session_id
            )

            if result["success"]:
                print("✅ LangGraph processing completed successfully!")

                # Convert workflow results back to ProcessingResult objects
                player_results = []
                for raw_result in result["results"]:
                    processing_result = ProcessingResult(
                        player_name=raw_result.get("player_name", "Unknown"),
                        total_cost=raw_result.get("total_cost", 0.0),
                        selected_ingredients=raw_result.get("selected_ingredients", []),
                        image_instructions=raw_result.get("image_instructions", {}),
                        reasoning_steps=raw_result.get("reasoning_steps", []),
                        processing_errors=raw_result.get("processing_errors", []),
                        cost_validation=raw_result.get("cost_validation", {}),
                        personality_enhancement=raw_result.get(
                            "personality_enhancement"
                        ),
                    )
                    player_results.append(processing_result)

                return GameProcessingResult(
                    game_date=str(game_data.gameDate),
                    total_players=len(player_results),
                    player_results=player_results,
                    group_summary=result.get("group_summary"),
                    processing_time=(datetime.now() - start_time).total_seconds(),
                    session_id=session_id,
                    total_cost=sum(r.total_cost for r in player_results),
                    processing_errors=result.get("processing_errors", []),
                    metadata={
                        "workflow_type": "langgraph",
                        "thread_id": session_id,
                        "has_errors": result["workflow_metadata"]["has_errors"],
                    },
                )
            else:
                raise Exception(
                    f"LangGraph processing failed: {result.get('error', 'Unknown error')}"
                )

        except Exception as e:
            print(f"❌ Error in LangGraph processing: {str(e)}")
            return GameProcessingResult(
                game_date=str(game_data.gameDate),
                total_players=0,
                player_results=[],
                processing_time=(datetime.now() - start_time).total_seconds(),
                session_id=session_id,
                total_cost=0.0,
                processing_errors=[f"LangGraph workflow error: {str(e)}"],
                metadata={"workflow_type": "langgraph", "error": str(e)},
            )

    async def _process_with_direct_agents(
        self, game_data: GameData
    ) -> GameProcessingResult:
        """Process game data using direct agent calls (fallback method)."""
        start_time = datetime.now()
        session_id = f"game_{game_data.gameDate.strftime('%Y%m%d_%H%M%S')}"

        # Start reasoning trace
        self.reasoning_tracer.start_trace(
            session_id=session_id,
            metadata={
                "total_players": game_data.totalPlayers,
                "game_date": str(game_data.gameDate),
                "game_version": game_data.gameVersion,
            },
        )

        # Process all players
        player_results = await self.game_adapter.process_game_data(game_data)

        # Create game processing result
        game_result = GameProcessingResult(
            game_date=str(game_data.gameDate),
            total_players=game_data.totalPlayers,
            player_results=player_results,
            processing_time=(datetime.now() - start_time).total_seconds(),
            session_id=session_id,
            total_cost=sum(r.total_cost for r in player_results),
            metadata={"workflow_type": "direct_agents"},
        )

        # Generate game summary
        game_result.group_summary = self._generate_game_summary(
            game_data, player_results
        )

        # Add final reasoning step
        self.reasoning_tracer.add_step(
            action="complete_game_processing",
            input_data={"total_players": game_data.totalPlayers},
            output_data={
                "successful_players": len(player_results),
                "total_time": game_result.processing_time,
            },
            reasoning=f"Completed processing game with {len(player_results)} players in {game_result.processing_time:.2f} seconds",
        )

        return game_result

    async def process_single_player(self, player_data: PlayerData) -> ProcessingResult:
        """
        Process individual player's selections (for testing or single-player scenarios).
        """
        session_id = f"player_{player_data.id}_{datetime.now().strftime('%H%M%S')}"

        self.reasoning_tracer.start_trace(
            session_id=session_id,
            metadata={"player_id": player_data.id, "player_name": player_data.name},
        )

        result = await self.game_adapter.process_single_player(player_data)

        # Add reasoning trace to result
        result.reasoning_steps.extend(self.reasoning_tracer.get_trace())

        return result

    async def calculate_all_player_costs(self, game_data: GameData) -> Dict[str, Any]:
        """
        Calculate authoritative costs for all players from backend database (ignores frontend).
        """
        calculation_results = {}

        for player in game_data.players:
            cost_calculation = await self.mcp_client.calculate_total_cost(
                player.selections
            )
            calculation_results[player.id] = {
                "player_name": player.name,
                "authoritative_cost": cost_calculation.calculated_cost,
                "cost_details": cost_calculation.details,
                "status": cost_calculation.validation_status,
            }

        return calculation_results

    async def get_available_selection_mappings(self) -> List[Dict[str, Any]]:
        """
        Get available abstract selection mappings (Rich, Crunchy, etc.).
        """
        return self.selection_mapper.get_available_selections()

    async def validate_all_player_costs(self, game_data: GameData) -> Dict[str, Any]:
        """
        Calculate authoritative costs using backend database for all players.
        """
        validation_results = []

        for player in game_data.players:
            try:
                # Calculate backend cost
                cost_validation = await self.mcp_client.calculate_total_cost(
                    player.selections
                )

                # Compare with frontend
                frontend_cost = player.totalCost
                backend_cost = cost_validation.calculated_cost

                validation_results.append(
                    {
                        "player_id": player.id,
                        "player_name": player.name,
                        "frontend_cost": frontend_cost,
                        "backend_cost": backend_cost,
                        "difference": abs(frontend_cost - backend_cost),
                        "validation_status": "FRONTEND_IGNORED",
                        "calculation_method": "ingredient_database",
                    }
                )

            except Exception as e:
                validation_results.append(
                    {
                        "player_id": player.id,
                        "player_name": player.name,
                        "error": str(e),
                        "validation_status": "ERROR",
                    }
                )

        return {
            "validation_results": validation_results,
            "total_players": len(game_data.players),
            "backend_authoritative": True,
        }

    async def get_game_reasoning_report(self, game_date: str) -> str:
        """
        Get detailed reasoning report for entire game session.
        """
        return self.reasoning_tracer.export_debug_report()

    def _generate_game_summary(
        self, game_data: GameData, results: List[ProcessingResult]
    ) -> Dict[str, Any]:
        """Generate summary statistics for the game processing."""
        successful_results = [r for r in results if not r.processing_errors]

        # Calculate cost statistics
        total_frontend_cost = sum(r.cost_validation.frontend_cost for r in results)
        total_calculated_cost = sum(r.cost_validation.calculated_cost for r in results)
        discrepancies = [r for r in results if r.cost_validation.has_discrepancy]

        # Selection analysis
        all_selections = []
        for player in game_data.players:
            all_selections.extend([s for s in player.selections if s.lower() != "skip"])

        selection_counts = {}
        for selection in all_selections:
            selection_counts[selection] = selection_counts.get(selection, 0) + 1

        # Processing performance
        avg_processing_time = (
            sum(r.processing_time for r in results) / len(results) if results else 0
        )

        return {
            "successful_players": len(successful_results),
            "failed_players": len(results) - len(successful_results),
            "players_with_valid_selections": len(
                [p for p in game_data.players if game_data.has_valid_selections(p.id)]
            ),
            "players_with_all_skips": len(
                [
                    p
                    for p in game_data.players
                    if not game_data.has_valid_selections(p.id)
                ]
            ),
            "cost_summary": {
                "total_frontend_cost": total_frontend_cost,
                "total_calculated_cost": total_calculated_cost,
                "total_difference": total_calculated_cost - total_frontend_cost,
                "players_with_discrepancies": len(discrepancies),
                "largest_discrepancy": max(
                    (abs(r.cost_validation.difference) for r in discrepancies),
                    default=0.0,
                ),
            },
            "selection_analysis": {
                "total_non_skip_selections": len(all_selections),
                "unique_selections": len(set(all_selections)),
                "most_popular_selection": max(
                    selection_counts.items(), key=lambda x: x[1]
                )[0]
                if selection_counts
                else None,
                "selection_counts": selection_counts,
            },
            "performance": {
                "average_processing_time": avg_processing_time,
                "fastest_player": min(r.processing_time for r in results)
                if results
                else 0,
                "slowest_player": max(r.processing_time for r in results)
                if results
                else 0,
            },
        }

    async def analyze_game_patterns(self, game_data: GameData) -> Dict[str, Any]:
        """Analyze patterns in the game data for insights."""
        patterns = {
            "skip_patterns": {},
            "selection_patterns": {},
            "personality_patterns": {},
            "cost_patterns": {},
        }

        # Analyze skip patterns
        for player in game_data.players:
            skip_count = sum(1 for s in player.selections if s.lower() == "skip")
            skip_percentage = (skip_count / len(player.selections)) * 100

            patterns["skip_patterns"][player.id] = {
                "skip_count": skip_count,
                "skip_percentage": skip_percentage,
                "skip_pattern": "high_skipper"
                if skip_percentage > 75
                else "moderate_skipper"
                if skip_percentage > 50
                else "active_player",
            }

        # Analyze selection diversity
        all_non_skip = []
        for player in game_data.players:
            player_selections = [s for s in player.selections if s.lower() != "skip"]
            all_non_skip.extend(player_selections)

        unique_selections = set(all_non_skip)
        patterns["selection_patterns"] = {
            "total_selections": len(all_non_skip),
            "unique_selections": len(unique_selections),
            "selection_diversity": len(unique_selections) / len(all_non_skip)
            if all_non_skip
            else 0,
            "popular_selections": {
                sel: all_non_skip.count(sel) for sel in unique_selections
            },
        }

        # Analyze personality types
        personality_types = {}
        for player in game_data.players:
            personality_name = player.personality.name
            if personality_name not in personality_types:
                personality_types[personality_name] = 0
            personality_types[personality_name] += 1

        patterns["personality_patterns"] = personality_types

        # Analyze cost patterns using backend-calculated costs
        calculated_costs = []
        for player in game_data.players:
            cost_calc = await self.cost_calculator.calculate_authoritative_cost(
                player.selections
            )
            calculated_costs.append(cost_calc)

        patterns["cost_patterns"] = {
            "average_cost": sum(calculated_costs) / len(calculated_costs)
            if calculated_costs
            else 0,
            "min_cost": min(calculated_costs) if calculated_costs else 0,
            "max_cost": max(calculated_costs) if calculated_costs else 0,
            "cost_range": max(calculated_costs) - min(calculated_costs)
            if calculated_costs
            else 0,
            "backend_calculated": True,
        }

        return patterns
