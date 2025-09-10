"""Enhanced MCP client for game-based cost calculations."""

import json
from typing import Dict, List, Optional, Any
import aiosqlite
from src.settings import DB_FILE
from src.models.processing_result import CostValidation
from src.models.game_data import PlayerData, PersonalityProfile


class MCPClient:
    """Enhanced MCP client for game-based ice cream processing."""

    # Mapping of abstract game selections to concrete ingredients
    SELECTION_MAPPINGS = {
        "rich": {
            "flavors": ["chocolate", "mascarpone", "caramel"],
            "toppings": ["chocolate_sauce", "caramel_drizzle", "brownie_pieces"],
            "premium_factor": 1.5,
            "description": "Rich, indulgent flavors and premium toppings",
        },
        "crunchy": {
            "flavors": ["cookies", "nuts"],
            "toppings": ["chocolate_chips", "crushed_cookies", "hazelnuts", "almonds"],
            "texture_focus": True,
            "description": "Textured ingredients with satisfying crunch",
        },
        "sweet": {
            "flavors": ["vanilla", "strawberry", "caramel"],
            "toppings": ["sprinkles", "caramel_drizzle", "honey"],
            "description": "Classic sweet flavors and toppings",
        },
        "fruity": {
            "flavors": ["strawberry", "lemon"],
            "toppings": ["fresh_berries", "fruit_syrup"],
            "description": "Fresh, fruity flavors",
        },
        "skip": {
            "action": "exclude_or_simplify",
            "impact": "minimal_addition",
            "description": "No impact or minimal vanilla base",
        },
    }

    def __init__(self):
        """Initialize MCP client."""
        pass

    async def get_all_ingredients(self) -> List[Dict[str, Any]]:
        """Get all available ingredients from database."""
        async with aiosqlite.connect(DB_FILE) as db:
            cursor = await db.execute("SELECT * FROM inventory")
            rows = await cursor.fetchall()
            columns = [column[0] for column in cursor.description]
            return [dict(zip(columns, row)) for row in rows]

    async def get_ingredient_by_name(
        self, ingredient_name: str
    ) -> Optional[Dict[str, Any]]:
        """Get specific ingredient details."""
        async with aiosqlite.connect(DB_FILE) as db:
            cursor = await db.execute(
                "SELECT * FROM inventory WHERE LOWER(ingredient) LIKE LOWER(?)",
                (f"%{ingredient_name}%",),
            )
            row = await cursor.fetchone()
            if row:
                columns = [column[0] for column in cursor.description]
                return dict(zip(columns, row))
        return None

    async def map_selection_to_ingredients(self, selection: str) -> List[str]:
        """Map abstract selections like 'Rich', 'Crunchy' to actual ingredients."""
        selection_lower = selection.lower()

        if selection_lower == "skip":
            return []

        if selection_lower not in self.SELECTION_MAPPINGS:
            # If selection doesn't match known mappings, try to find similar ingredients
            return await self._find_similar_ingredients(selection)

        mapping = self.SELECTION_MAPPINGS[selection_lower]
        ingredients = []

        # Add flavors
        for flavor in mapping.get("flavors", []):
            ingredient = await self._find_ingredient_by_keyword(flavor)
            if ingredient:
                ingredients.append(ingredient["ingredient"])

        # Add toppings
        for topping in mapping.get("toppings", []):
            ingredient = await self._find_ingredient_by_keyword(topping)
            if ingredient:
                ingredients.append(ingredient["ingredient"])

        return ingredients

    async def _find_ingredient_by_keyword(
        self, keyword: str
    ) -> Optional[Dict[str, Any]]:
        """Find ingredient that matches a keyword."""
        async with aiosqlite.connect(DB_FILE) as db:
            # Try exact match first
            cursor = await db.execute(
                "SELECT * FROM inventory WHERE LOWER(ingredient) LIKE LOWER(?)",
                (f"%{keyword}%",),
            )
            row = await cursor.fetchone()
            if row:
                columns = [column[0] for column in cursor.description]
                return dict(zip(columns, row))

            # Try description match
            cursor = await db.execute(
                "SELECT * FROM inventory WHERE LOWER(description) LIKE LOWER(?)",
                (f"%{keyword}%",),
            )
            row = await cursor.fetchone()
            if row:
                columns = [column[0] for column in cursor.description]
                return dict(zip(columns, row))

        return None

    async def _find_similar_ingredients(self, selection: str) -> List[str]:
        """Find ingredients similar to an unknown selection."""
        ingredients = await self.get_all_ingredients()
        similar = []

        for ingredient in ingredients:
            # Check if selection appears in ingredient name or description
            if (
                selection.lower() in ingredient["ingredient"].lower()
                or selection.lower() in (ingredient.get("description", "")).lower()
            ):
                similar.append(ingredient["ingredient"])

        return similar[:3]  # Return top 3 matches

    async def get_cost_for_abstract_selection(self, selection: str) -> Dict[str, float]:
        """Calculate cost for abstract selections like 'Rich' or 'Crunchy'."""
        ingredients = await self.map_selection_to_ingredients(selection)
        cost_breakdown = {}

        for ingredient_name in ingredients:
            ingredient = await self.get_ingredient_by_name(ingredient_name)
            if ingredient and ingredient.get("cost_min") is not None:
                # Use average of min and max cost, or just min if max is None
                cost_max = ingredient.get("cost_max") or ingredient.get("cost_min")
                avg_cost = (ingredient["cost_min"] + cost_max) / 2
                cost_breakdown[ingredient_name] = avg_cost

        return cost_breakdown

    async def calculate_ingredients_cost(
        self, ingredients: List[str]
    ) -> Dict[str, float]:
        """Calculate cost for a list of specific ingredients."""
        cost_breakdown = {}

        for ingredient_name in ingredients:
            ingredient = await self.get_ingredient_by_name(ingredient_name)
            if ingredient and ingredient.get("cost_min") is not None:
                cost_max = ingredient.get("cost_max") or ingredient.get("cost_min")
                avg_cost = (ingredient["cost_min"] + cost_max) / 2
                cost_breakdown[ingredient_name] = avg_cost

        return cost_breakdown

    async def calculate_total_cost(self, selections: List[str]) -> CostValidation:
        """Calculate authoritative total cost from backend database (frontend costs ignored)."""
        total_calculated_cost = 0.0
        cost_details = []

        for selection in selections:
            if selection.lower() != "skip":
                selection_costs = await self.get_cost_for_abstract_selection(selection)
                total_calculated_cost += sum(selection_costs.values())
                cost_details.extend(
                    [
                        f"{ingredient}: ${cost:.2f}"
                        for ingredient, cost in selection_costs.items()
                    ]
                )

        details = (
            f"Calculated from: {'; '.join(cost_details)}"
            if cost_details
            else "No ingredients found"
        )

        return CostValidation(
            frontend_cost=0.0,  # Frontend costs are ignored
            calculated_cost=total_calculated_cost,
            difference=0.0,  # No comparison needed
            validation_status="FRONTEND_IGNORED",
            details=details,
        )

    async def get_ingredients_for_personality(
        self, personality: PersonalityProfile
    ) -> List[str]:
        """Suggest ingredients based on personality profile."""
        suggested_ingredients = []

        # Analyze personality traits for ingredient suggestions
        personality_text = f"{personality.name} {personality.description} {' '.join(personality.insights)}".lower()

        # Mapping of personality traits to ingredient preferences
        trait_mappings = {
            "mysterious": ["dark chocolate", "blackberry", "espresso"],
            "unpredictable": ["exotic fruits", "unusual flavors"],
            "skip": ["vanilla", "simple"],
            "rich": ["mascarpone", "chocolate", "caramel"],
            "crunchy": ["nuts", "cookies", "chips"],
            "sweet": ["vanilla", "strawberry", "honey"],
            "dramatic": ["bold colors", "intense flavors"],
            "minimalist": ["vanilla", "simple", "clean"],
        }

        for trait, ingredients in trait_mappings.items():
            if trait in personality_text:
                for ingredient_keyword in ingredients:
                    ingredient = await self._find_ingredient_by_keyword(
                        ingredient_keyword
                    )
                    if (
                        ingredient
                        and ingredient["ingredient"] not in suggested_ingredients
                    ):
                        suggested_ingredients.append(ingredient["ingredient"])

        return suggested_ingredients[:5]  # Return top 5 suggestions

    async def get_allergy_warnings(self, ingredients: List[str]) -> List[str]:
        """Get allergy warnings for a list of ingredients."""
        all_allergies = set()

        for ingredient_name in ingredients:
            ingredient = await self.get_ingredient_by_name(ingredient_name)
            if ingredient and ingredient.get("allergies"):
                try:
                    allergies = json.loads(ingredient["allergies"])
                    all_allergies.update(allergies)
                except (json.JSONDecodeError, TypeError):
                    # Handle non-JSON allergy data
                    allergy_str = str(ingredient["allergies"]).strip("[]'\"")
                    if allergy_str:
                        all_allergies.add(allergy_str)

        return list(all_allergies)

    async def calculate_multi_player_cost(
        self, players: List[PlayerData]
    ) -> Dict[str, float]:
        """Calculate authoritative costs for multiple players (frontend costs ignored)."""
        player_costs = {}

        for player in players:
            cost_calculation = await self.calculate_total_cost(player.selections)
            player_costs[player.id] = cost_calculation.calculated_cost

        return player_costs

    async def get_available_flavors(self) -> List[str]:
        """Get all available flavors from used_on field."""
        async with aiosqlite.connect(DB_FILE) as db:
            cursor = await db.execute(
                "SELECT used_on FROM inventory WHERE used_on != '[]'"
            )
            rows = await cursor.fetchall()

            all_flavors = set()
            for row in rows:
                try:
                    flavors = json.loads(row[0])
                    all_flavors.update(flavors)
                except (json.JSONDecodeError, TypeError):
                    # Handle non-JSON data
                    flavor_str = row[0].strip("[]'\"")
                    if flavor_str:
                        all_flavors.add(flavor_str)

            return list(all_flavors)

    async def decrease_ingredient_inventory(
        self, ingredient_name: str, amount: int = 1
    ) -> bool:
        """Decrease inventory for an ingredient."""
        async with aiosqlite.connect(DB_FILE) as db:
            cursor = await db.execute(
                "UPDATE inventory SET inventory = inventory - ? WHERE ingredient = ? AND inventory >= ?",
                (amount, ingredient_name, amount),
            )
            await db.commit()
            return cursor.rowcount > 0
