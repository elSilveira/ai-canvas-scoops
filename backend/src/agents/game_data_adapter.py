"""Game Data Adapter Agent for processing game-based ice cream selections."""

from datetime import datetime
from typing import Dict, List, Any, Optional
from pydantic_ai import Agent

from src.models.game_data import GameData, PlayerData, PersonalityProfile
from src.models.processing_result import ProcessingResult, CostValidation
from src.models.reasoning_step import ReasoningStep
from src.models.image_instructions import ImageInstructions
from src.tools.mcp_client import MCPClient


class GameDataAdapterAgent:
    """
    Specialized LLM agent for processing game-based ice cream selections:
    1. Interpreting abstract selections (Rich, Crunchy, Skip)
    2. Mapping personality profiles to flavor preferences
    3. Handling multi-player scenarios
    4. Validating costs against game calculations
    """

    def __init__(self):
        self.mcp_client = MCPClient()
        self.reasoning_steps: List[ReasoningStep] = []

        # Initialize the Pydantic-AI agent with ReAct framework
        self.agent = Agent(
            "openai:gpt-4o",  # Using GPT-4o as specified in existing code
            system_prompt="""You are an expert ice cream advisor that follows the ReAct (Reasoning + Acting) framework 
            to transform abstract game selections into concrete ice cream specifications.
            
            ALWAYS follow this ReAct pattern in your reasoning:
            1. THOUGHT: Analyze the current situation and decide what to do next
            2. ACTION: Execute a specific operation (map selections, apply personality, calculate costs, etc.)
            3. OBSERVATION: Process and understand the results of your action
            4. REFLECTION: Evaluate if your goal is achieved or determine next steps
            
            Your ReAct responsibilities:
            - THOUGHT: "The player selected 'Rich' - I need to interpret this as luxury ice cream components"
            - ACTION: Map "Rich" to premium ingredients like dark chocolate, mascarpone, premium toppings
            - OBSERVATION: "Found chocolate, mascarpone, caramel as Rich ingredients with costs X, Y, Z"
            - REFLECTION: "These ingredients create a rich experience, cost is reasonable, proceeding to next step"
            
            Apply ReAct to:
            1. Interpret abstract selections (Rich, Crunchy, Skip) → concrete ingredients
            2. Apply personality insights to enhance flavor choices
            3. Validate ingredient availability and costs
            4. Generate final ice cream specifications
            
            Document each THOUGHT → ACTION → OBSERVATION → REFLECTION cycle clearly.
            """,
        )

    async def process_game_data(self, game_data: GameData) -> List[ProcessingResult]:
        """Process complete game data for all players."""
        results = []
        start_time = datetime.now()

        self._add_reasoning_step(
            action="start_game_processing",
            input_data={
                "total_players": game_data.totalPlayers,
                "game_date": str(game_data.gameDate),
            },
            output_data={},
            reasoning=f"Starting processing for {game_data.totalPlayers} players from game on {game_data.gameDate}",
        )

        for player in game_data.players:
            try:
                player_result = await self.process_single_player(player)
                results.append(player_result)

                self._add_reasoning_step(
                    action="complete_player_processing",
                    input_data={"player_id": player.id},
                    output_data={"total_cost": player_result.total_cost},
                    reasoning=f"Completed processing for player {player.name} with total cost ${player_result.total_cost:.2f}",
                )

            except Exception as e:
                # Create error result for failed processing
                error_result = ProcessingResult(
                    player_id=player.id,
                    player_name=player.name,
                    image_instructions=ImageInstructions(scoops=1, flavors=["vanilla"]),
                    total_cost=0.0,
                    cost_validation=CostValidation(
                        frontend_cost=player.totalCost,
                        calculated_cost=0.0,
                        difference=-player.totalCost,
                        validation_status="ERROR",
                    ),
                    processing_errors=[f"Failed to process player: {str(e)}"],
                )
                results.append(error_result)

        end_time = datetime.now()
        processing_time = (end_time - start_time).total_seconds()

        # Update processing times
        for result in results:
            result.processing_time = processing_time / len(results)

        return results

    async def process_single_player(self, player: PlayerData) -> ProcessingResult:
        """Process individual player's selections and generate ice cream."""
        start_time = datetime.now()

        # Initialize result
        result = ProcessingResult(
            player_id=player.id,
            player_name=player.name,
            image_instructions=ImageInstructions(scoops=1, flavors=["vanilla"]),
            total_cost=0.0,
            cost_validation=CostValidation(
                frontend_cost=player.totalCost,
                calculated_cost=0.0,
                difference=0.0,
                validation_status="PENDING",
            ),
        )

        try:
            # Step 1: Interpret abstract selections
            interpretation = await self.interpret_abstract_selections(player.selections)
            result.add_reasoning_step(
                ReasoningStep(
                    step_number=1,
                    action="interpret_selections",
                    input_data={"selections": player.selections},
                    output_data=interpretation,
                    reasoning="Mapped player selections to concrete ice cream components",
                    game_context=f"Player {player.name} selected: {', '.join(player.selections)}",
                )
            )

            # Step 2: Apply personality influence
            enhanced_specs = await self.apply_personality_influence(
                interpretation, player.personality
            )
            result.add_reasoning_step(
                ReasoningStep(
                    step_number=2,
                    action="apply_personality_influence",
                    input_data={
                        "base_specs": interpretation,
                        "personality": player.personality.name,
                    },
                    output_data=enhanced_specs,
                    reasoning=f"Enhanced ice cream based on personality: {player.personality.name}",
                    game_context=f"Personality insights: {', '.join(player.personality.insights)}",
                )
            )

            # Step 3: Validate costs
            cost_validation = await self.validate_game_cost(
                player.selections, player.totalCost
            )
            result.cost_validation = cost_validation
            result.total_cost = cost_validation.calculated_cost
            result.add_reasoning_step(
                ReasoningStep(
                    step_number=3,
                    action="validate_cost",
                    input_data={
                        "selections": player.selections,
                        "frontend_cost": player.totalCost,
                    },
                    output_data={
                        "validation_status": cost_validation.validation_status,
                        "calculated_cost": cost_validation.calculated_cost,
                    },
                    reasoning=f"Cost validation: {cost_validation.validation_status}, difference: ${cost_validation.difference:.2f}",
                )
            )

            # Step 4: Generate final image instructions
            image_instructions = await self.create_image_instructions(
                enhanced_specs, player.personality
            )
            result.image_instructions = image_instructions

            # Step 5: Get additional metadata
            all_ingredients = enhanced_specs.get("flavors", []) + enhanced_specs.get(
                "toppings", []
            )
            result.selected_ingredients = all_ingredients
            result.allergy_warnings = await self.mcp_client.get_allergy_warnings(
                all_ingredients
            )
            result.personality_influence = enhanced_specs.get(
                "personality_enhancements", {}
            )

            # Calculate cost breakdown
            if all_ingredients:
                result.cost_breakdown = (
                    await self.mcp_client.calculate_ingredients_cost(all_ingredients)
                )

        except Exception as e:
            result.processing_errors.append(f"Error processing player: {str(e)}")

        end_time = datetime.now()
        result.processing_time = (end_time - start_time).total_seconds()

        return result

    async def interpret_abstract_selections(
        self, selections: List[str]
    ) -> Dict[str, Any]:
        """Map abstract game selections to concrete ice cream components."""
        non_skip_selections = [sel for sel in selections if sel.lower() != "skip"]

        if not non_skip_selections:
            # All skips - return minimal ice cream
            return {
                "flavors": ["vanilla"],
                "toppings": [],
                "scoops": 1,
                "interpretation": "Player skipped all selections, defaulting to simple vanilla",
            }

        all_flavors = []
        all_toppings = []
        interpretation_notes = []

        for selection in non_skip_selections:
            ingredients = await self.mcp_client.map_selection_to_ingredients(selection)

            # Categorize ingredients as flavors or toppings
            flavors, toppings = await self._categorize_ingredients(ingredients)
            all_flavors.extend(flavors)
            all_toppings.extend(toppings)

            interpretation_notes.append(
                f"'{selection}' → flavors: {flavors}, toppings: {toppings}"
            )

        # Remove duplicates while preserving order
        unique_flavors = list(dict.fromkeys(all_flavors))
        unique_toppings = list(dict.fromkeys(all_toppings))

        # Determine number of scoops based on selections
        scoops = min(len(non_skip_selections), 3)  # Max 3 scoops
        scoops = max(scoops, 1)  # Min 1 scoop

        return {
            "flavors": unique_flavors or ["vanilla"],  # Fallback to vanilla
            "toppings": unique_toppings,
            "scoops": scoops,
            "interpretation": "; ".join(interpretation_notes),
            "non_skip_count": len(non_skip_selections),
        }

    async def _categorize_ingredients(
        self, ingredients: List[str]
    ) -> tuple[List[str], List[str]]:
        """Categorize ingredients as flavors or toppings."""
        flavors = []
        toppings = []

        # Keywords to identify toppings vs flavors
        topping_keywords = [
            "chips",
            "sauce",
            "drizzle",
            "pieces",
            "nuts",
            "sprinkles",
            "crumbs",
        ]

        for ingredient in ingredients:
            ingredient_lower = ingredient.lower()
            if any(keyword in ingredient_lower for keyword in topping_keywords):
                toppings.append(ingredient)
            else:
                flavors.append(ingredient)

        return flavors, toppings

    async def apply_personality_influence(
        self, base_specs: Dict[str, Any], personality: PersonalityProfile
    ) -> Dict[str, Any]:
        """Enhance ice cream specs based on personality profile."""
        enhanced_specs = base_specs.copy()
        personality_enhancements = {}

        # Get personality-suggested ingredients
        personality_ingredients = await self.mcp_client.get_ingredients_for_personality(
            personality
        )

        # Apply personality-based enhancements
        personality_text = f"{personality.name} {personality.description}".lower()

        if "mysterious" in personality_text:
            # Add dramatic colors or unusual combinations
            personality_enhancements["color_theme"] = "dark and mysterious"
            personality_enhancements["visual_style"] = "dramatic contrast"

        if "unpredictable" in personality_text or "skip" in personality_text:
            # Add unexpected elements
            personality_enhancements["surprise_element"] = (
                "unexpected color combinations"
            )

        if "rich" in personality_text:
            # Enhance with premium ingredients
            if personality_ingredients:
                enhanced_specs["flavors"].extend(personality_ingredients[:2])
                personality_enhancements["enhancement"] = "added premium ingredients"

        # Add personality influence to specs
        enhanced_specs["personality_enhancements"] = personality_enhancements
        enhanced_specs["personality_suggested_ingredients"] = personality_ingredients

        return enhanced_specs

    async def calculate_game_cost(self, selections: List[str]) -> CostValidation:
        """Calculate authoritative cost from backend database (ignores frontend)."""
        return await self.mcp_client.calculate_total_cost(selections)

    async def validate_game_cost(
        self, selections: List[str], claimed_cost: float
    ) -> CostValidation:
        """Cross-check game-calculated costs with ingredient database (deprecated - use calculate_game_cost)."""
        return await self.mcp_client.validate_frontend_cost(selections, claimed_cost)

    async def create_image_instructions(
        self, specs: Dict[str, Any], personality: PersonalityProfile
    ) -> ImageInstructions:
        """Create ImageInstructions based on processed specs and personality."""
        # Extract core components
        flavors = specs.get("flavors", ["vanilla"])[:3]  # Max 3 flavors
        toppings = specs.get("toppings", [])[:5]  # Max 5 toppings
        scoops = specs.get("scoops", 1)

        # Apply personality influence to visual aspects
        image_instructions = ImageInstructions(
            scoops=scoops, flavors=flavors, toppings=toppings
        )

        return image_instructions

    def _add_reasoning_step(
        self,
        action: str,
        input_data: Dict[str, Any],
        output_data: Dict[str, Any],
        reasoning: str,
        game_context: Optional[str] = None,
    ) -> None:
        """Add a reasoning step to the trace."""
        step = ReasoningStep(
            step_number=len(self.reasoning_steps) + 1,
            action=action,
            input_data=input_data,
            output_data=output_data,
            reasoning=reasoning,
            game_context=game_context,
        )
        self.reasoning_steps.append(step)

    def get_reasoning_trace(self) -> List[ReasoningStep]:
        """Get the complete reasoning trace."""
        return self.reasoning_steps.copy()

    def clear_reasoning_trace(self) -> None:
        """Clear the reasoning trace for a new session."""
        self.reasoning_steps.clear()
