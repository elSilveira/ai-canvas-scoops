"""Selection Mapping Agent for abstract game selections to ingredients."""

from typing import Dict, List, Any
from pydantic_ai import Agent
from src.tools.mcp_client import MCPClient


class SelectionMappingAgent:
    """Specialized agent for mapping abstract game selections to ingredients."""

    # Enhanced selection mappings with more detailed specifications
    SELECTION_MAPPINGS = {
        "rich": {
            "flavors": ["chocolate", "mascarpone", "caramel", "espresso"],
            "toppings": ["chocolate_sauce", "caramel_drizzle", "brownie_pieces"],
            "premium_factor": 1.5,
            "description": "Rich, indulgent flavors with premium ingredients",
            "keywords": ["luxurious", "decadent", "indulgent", "premium"],
            "color_palette": ["dark brown", "gold", "deep amber"],
        },
        "crunchy": {
            "flavors": ["cookies", "nuts", "praline"],
            "toppings": [
                "chocolate_chips",
                "crushed_cookies",
                "hazelnuts",
                "almonds",
                "granola",
            ],
            "texture_focus": True,
            "description": "Textured ingredients with satisfying crunch",
            "keywords": ["textured", "crispy", "nutty", "cookie"],
            "sound_profile": "satisfying crunch",
        },
        "sweet": {
            "flavors": ["vanilla", "strawberry", "caramel", "honey"],
            "toppings": [
                "sprinkles",
                "caramel_drizzle",
                "honey_drizzle",
                "sugar_crystals",
            ],
            "sweetness_level": "high",
            "description": "Classic sweet flavors and toppings",
            "keywords": ["sugary", "candy", "dessert", "treat"],
            "color_palette": ["pastel pink", "golden yellow", "pure white"],
        },
        "fruity": {
            "flavors": ["strawberry", "lemon", "raspberry", "mango"],
            "toppings": ["fresh_berries", "fruit_syrup", "citrus_zest"],
            "freshness_factor": True,
            "description": "Fresh, fruity flavors with natural sweetness",
            "keywords": ["fresh", "natural", "zesty", "bright"],
            "color_palette": ["vibrant red", "sunny yellow", "fresh green"],
        },
        "creamy": {
            "flavors": ["vanilla", "mascarpone", "cream", "custard"],
            "toppings": ["whipped_cream", "cream_sauce"],
            "texture": "smooth",
            "description": "Smooth, creamy textures and mild flavors",
            "keywords": ["smooth", "silky", "mild", "gentle"],
            "mouthfeel": "velvety",
        },
        "spicy": {
            "flavors": ["cinnamon", "ginger", "cardamom"],
            "toppings": ["spiced_nuts", "cinnamon_dust"],
            "heat_level": "mild",
            "description": "Warm spices for adventurous palates",
            "keywords": ["warm", "exotic", "aromatic", "bold"],
            "temperature_contrast": True,
        },
        "skip": {
            "action": "exclude_or_simplify",
            "impact": "minimal_addition",
            "description": "No impact or minimal vanilla base",
            "default_fallback": ["vanilla"],
            "reasoning": "Player chose not to make a selection this round",
        },
    }

    def __init__(self):
        self.mcp_client = MCPClient()

        # Initialize the mapping agent with ReAct framework
        self.agent = Agent(
            "openai:gpt-4o",
            system_prompt="""You are an expert ice cream flavor architect that follows the ReAct framework 
            (Reasoning + Acting) to translate abstract concepts into concrete, delicious ice cream specifications.
            
            ALWAYS apply ReAct reasoning to your mapping decisions:
            1. THOUGHT: Analyze the abstract selection and understand player intent
            2. ACTION: Map selection to specific ingredients using database and mappings
            3. OBSERVATION: Review ingredient choices for harmony and availability
            4. REFLECTION: Evaluate if mapping achieves player's desired experience
            
            ReAct examples for selection mapping:
            - THOUGHT: "Player selected 'Rich' - they want indulgent, premium experience"  
            - ACTION: Map to luxury ingredients: dark chocolate, mascarpone, caramel
            - OBSERVATION: "These ingredients create depth and premium feel, costs are higher"
            - REFLECTION: "Combination delivers rich experience without overwhelming, good choice"
            
            Your ReAct understanding of selections:
            - 'Rich': THOUGHT → luxury experience needed, ACTION → premium ingredients, OBSERVATION → cost implications, REFLECTION → balanced indulgence
            - 'Crunchy': THOUGHT → texture contrast desired, ACTION → nuts/cookies/chips, OBSERVATION → sound/mouthfeel, REFLECTION → satisfying bite achieved
            - 'Sweet': THOUGHT → classic dessert appeal, ACTION → vanilla/caramel/fruit, OBSERVATION → sweetness balance, REFLECTION → nostalgic satisfaction
            - 'Fruity': THOUGHT → fresh natural appeal, ACTION → real fruit ingredients, OBSERVATION → color/flavor harmony, REFLECTION → bright experience delivered
            - 'Skip': THOUGHT → minimal impact needed, ACTION → simple vanilla base, OBSERVATION → doesn't interfere, REFLECTION → allows other selections to shine
            
            Apply ReAct to create harmonious flavor combinations that satisfy the abstract concept while ensuring 
            the final ice cream is delicious, well-balanced, and achievable with available ingredients.
            """,
        )

    async def map_selection_to_components(self, selection: str) -> Dict[str, Any]:
        """Map a single selection to concrete ice cream components."""
        selection_lower = selection.lower()

        # Check if it's a known mapping
        if selection_lower in self.SELECTION_MAPPINGS:
            mapping = self.SELECTION_MAPPINGS[selection_lower].copy()

            # Enhance with actual ingredient data from database
            enhanced_mapping = await self._enhance_with_database_ingredients(mapping)
            return enhanced_mapping

        # For unknown selections, try to find similar patterns
        return await self._handle_unknown_selection(selection)

    async def _enhance_with_database_ingredients(
        self, mapping: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Enhance mapping with actual ingredients from database."""
        enhanced_mapping = mapping.copy()
        actual_flavors = []
        actual_toppings = []

        # Find actual ingredients for flavor keywords
        for flavor_keyword in mapping.get("flavors", []):
            ingredient = await self.mcp_client._find_ingredient_by_keyword(
                flavor_keyword
            )
            if ingredient:
                actual_flavors.append(ingredient["ingredient"])

        # Find actual ingredients for topping keywords
        for topping_keyword in mapping.get("toppings", []):
            ingredient = await self.mcp_client._find_ingredient_by_keyword(
                topping_keyword
            )
            if ingredient:
                actual_toppings.append(ingredient["ingredient"])

        enhanced_mapping["actual_flavors"] = actual_flavors
        enhanced_mapping["actual_toppings"] = actual_toppings
        enhanced_mapping["total_ingredients_found"] = len(actual_flavors) + len(
            actual_toppings
        )

        return enhanced_mapping

    async def _handle_unknown_selection(self, selection: str) -> Dict[str, Any]:
        """Handle selections that don't match known mappings."""
        # Try to find ingredients that match the selection
        similar_ingredients = await self.mcp_client._find_similar_ingredients(selection)

        # Create a basic mapping
        return {
            "flavors": [selection.lower()],
            "toppings": [],
            "actual_flavors": similar_ingredients[:2],  # Take top 2 matches
            "actual_toppings": similar_ingredients[2:4]
            if len(similar_ingredients) > 2
            else [],
            "description": f"Custom interpretation of '{selection}'",
            "is_custom": True,
            "confidence": "low" if not similar_ingredients else "medium",
        }

    async def calculate_selection_cost(self, selection: str) -> float:
        """Calculate cost for a specific selection."""
        components = await self.map_selection_to_components(selection)

        # Get ingredients for cost calculation
        all_ingredients = components.get("actual_flavors", []) + components.get(
            "actual_toppings", []
        )

        if not all_ingredients:
            return 0.0

        cost_breakdown = await self.mcp_client.calculate_ingredients_cost(
            all_ingredients
        )
        total_cost = sum(cost_breakdown.values())

        # Apply premium factor if specified
        premium_factor = components.get("premium_factor", 1.0)
        return total_cost * premium_factor

    async def get_selection_ingredients(self, selection: str) -> List[str]:
        """Get list of actual ingredients for a selection."""
        components = await self.map_selection_to_components(selection)
        return components.get("actual_flavors", []) + components.get(
            "actual_toppings", []
        )

    async def get_selection_description(self, selection: str) -> str:
        """Get detailed description of what a selection means."""
        components = await self.map_selection_to_components(selection)

        base_description = components.get(
            "description", f"Interpretation of '{selection}'"
        )

        # Add ingredient details if available
        actual_flavors = components.get("actual_flavors", [])
        actual_toppings = components.get("actual_toppings", [])

        if actual_flavors or actual_toppings:
            ingredient_detail = (
                f" Includes: {', '.join(actual_flavors + actual_toppings)}"
            )
            return base_description + ingredient_detail

        return base_description

    async def validate_selection_combination(
        self, selections: List[str]
    ) -> Dict[str, Any]:
        """Validate that a combination of selections works well together."""
        all_components = []
        total_cost = 0.0

        for selection in selections:
            if selection.lower() != "skip":
                components = await self.map_selection_to_components(selection)
                all_components.append(components)
                total_cost += await self.calculate_selection_cost(selection)

        # Analyze combination
        all_flavors = []
        all_toppings = []
        flavor_profiles = []

        for components in all_components:
            all_flavors.extend(components.get("actual_flavors", []))
            all_toppings.extend(components.get("actual_toppings", []))
            if "keywords" in components:
                flavor_profiles.extend(components["keywords"])

        # Check for conflicts (e.g., too many competing strong flavors)
        conflicts = []
        if len(set(all_flavors)) > 4:
            conflicts.append("Too many competing flavors")

        if len(set(all_toppings)) > 6:
            conflicts.append("Too many toppings")

        # Check for complementary profiles
        complementary = []
        if "rich" in [s.lower() for s in selections] and "crunchy" in [
            s.lower() for s in selections
        ]:
            complementary.append("Rich and crunchy make a great texture contrast")

        return {
            "total_cost": total_cost,
            "unique_flavors": list(set(all_flavors)),
            "unique_toppings": list(set(all_toppings)),
            "flavor_profiles": list(set(flavor_profiles)),
            "conflicts": conflicts,
            "complementary_aspects": complementary,
            "is_balanced": len(conflicts) == 0,
            "complexity_score": len(set(all_flavors)) + len(set(all_toppings)),
        }

    def get_available_selections(self) -> List[Dict[str, Any]]:
        """Get list of all available selection mappings."""
        return [
            {
                "selection": selection,
                "description": mapping.get("description", ""),
                "keywords": mapping.get("keywords", []),
                "example_flavors": mapping.get("flavors", [])[:3],
                "example_toppings": mapping.get("toppings", [])[:3],
            }
            for selection, mapping in self.SELECTION_MAPPINGS.items()
            if selection != "skip"
        ]

    async def suggest_combinations(self, base_selection: str) -> List[Dict[str, Any]]:
        """Suggest complementary selections for a base selection."""
        suggestions = []

        # Define complementary relationships
        complementary_pairs = {
            "rich": ["crunchy", "fruity"],
            "crunchy": ["rich", "creamy"],
            "sweet": ["fruity", "creamy"],
            "fruity": ["rich", "sweet"],
            "creamy": ["crunchy", "spicy"],
            "spicy": ["creamy", "sweet"],
        }

        base_lower = base_selection.lower()
        if base_lower in complementary_pairs:
            for complement in complementary_pairs[base_lower]:
                complement_components = await self.map_selection_to_components(
                    complement
                )
                suggestions.append(
                    {
                        "selection": complement,
                        "reason": f"Complements {base_selection} well",
                        "description": complement_components.get("description", ""),
                        "harmony_score": 0.8,  # Could be calculated based on flavor profiles
                    }
                )

        return suggestions
