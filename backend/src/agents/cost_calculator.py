"""Cost Calculator Agent for ice cream cost calculations using MCP tools."""

from typing import Dict, List, Any
from pydantic_ai import Agent
from src.tools.mcp_client import MCPClient


class CostCalculatorAgent:
    """Specialized agent for cost calculations using MCP tools."""

    def __init__(self):
        self.mcp_client = MCPClient()

        # Initialize the cost calculation agent with ReAct framework
        self.agent = Agent(
            "openai:gpt-4o",
            system_prompt="""You are an expert cost analyst for ice cream ingredients that follows the ReAct framework 
            (Reasoning + Acting) for systematic cost calculations and business analysis.
            
            ALWAYS apply ReAct reasoning to your cost calculations:
            1. THOUGHT: Analyze what cost calculation is needed and the business context
            2. ACTION: Execute specific cost operations (ingredient lookup, markup application, etc.)
            3. OBSERVATION: Process the cost data and understand the financial implications  
            4. REFLECTION: Evaluate if costs are reasonable and align with business objectives
            
            ReAct examples for cost analysis:
            - THOUGHT: "Player selected 'Rich' - need to determine premium ingredient costs"
            - ACTION: Query database for luxury ingredients like dark chocolate, mascarpone
            - OBSERVATION: "Retrieved costs: chocolate $0.50, mascarpone $0.48, markup needed"
            - REFLECTION: "Costs reflect premium quality, total reasonable for luxury ice cream"
            
            Your ReAct responsibilities:
            - Calculate accurate costs using database ingredient prices (AUTHORITATIVE source)
            - Apply appropriate markups based on ingredient premium level
            - Consider portion sizes and preparation complexity
            - Validate cost reasonableness against business rules
            - Provide detailed cost breakdowns with reasoning
            
            CRITICAL: Always ignore frontend totalCost values - calculate authoritatively from ingredient database.
            """,
        )

    async def calculate_flavor_costs(self, flavors: List[str]) -> Dict[str, float]:
        """Calculate cost for each flavor."""
        flavor_costs = {}

        for flavor in flavors:
            # Try to find exact ingredient match first
            ingredient = await self.mcp_client.get_ingredient_by_name(flavor)

            if ingredient and ingredient.get("cost_min") is not None:
                cost_min = ingredient["cost_min"]
                cost_max = ingredient.get("cost_max", cost_min)
                # Use average cost for calculation
                avg_cost = (cost_min + cost_max) / 2
                flavor_costs[flavor] = avg_cost
            else:
                # If exact match not found, try to map flavor to available ingredients
                mapped_ingredients = await self.mcp_client.map_selection_to_ingredients(
                    flavor
                )
                if mapped_ingredients:
                    # Calculate cost from mapped ingredients
                    ingredient_costs = await self.mcp_client.calculate_ingredients_cost(
                        mapped_ingredients
                    )
                    flavor_costs[flavor] = sum(ingredient_costs.values())
                else:
                    # Default cost if no ingredients found
                    flavor_costs[flavor] = 5.0  # Base ice cream cost

        return flavor_costs

    async def calculate_topping_costs(self, toppings: List[str]) -> Dict[str, float]:
        """Calculate cost for each topping."""
        topping_costs = {}

        for topping in toppings:
            # Get ingredient cost
            ingredient = await self.mcp_client.get_ingredient_by_name(topping)

            if ingredient and ingredient.get("cost_min") is not None:
                cost_min = ingredient["cost_min"]
                cost_max = ingredient.get("cost_max", cost_min)
                avg_cost = (cost_min + cost_max) / 2
                topping_costs[topping] = avg_cost
            else:
                # Try to find similar toppings
                mapped_ingredients = await self.mcp_client.map_selection_to_ingredients(
                    topping
                )
                if mapped_ingredients:
                    ingredient_costs = await self.mcp_client.calculate_ingredients_cost(
                        mapped_ingredients
                    )
                    topping_costs[topping] = sum(ingredient_costs.values())
                else:
                    # Default topping cost
                    topping_costs[topping] = 2.0  # Base topping cost

        return topping_costs

    async def get_total_with_breakdown(
        self, flavors: List[str], toppings: List[str], scoops: int
    ) -> Dict[str, Any]:
        """Get complete cost analysis."""
        # Calculate individual costs
        flavor_costs = await self.calculate_flavor_costs(flavors)
        topping_costs = await self.calculate_topping_costs(toppings)

        # Calculate base costs
        base_flavor_cost = sum(flavor_costs.values())
        base_topping_cost = sum(topping_costs.values())

        # Apply scoop multiplier to flavors (more scoops = more flavor)
        scoop_multiplier = max(1.0, scoops * 0.8)  # Each scoop adds 80% of base cost
        adjusted_flavor_cost = base_flavor_cost * scoop_multiplier

        # Calculate service and preparation costs
        preparation_cost = self._calculate_preparation_cost(len(flavors), len(toppings))
        service_cost = 1.0  # Base service cost

        # Calculate total
        subtotal = (
            adjusted_flavor_cost + base_topping_cost + preparation_cost + service_cost
        )

        # Apply any applicable markups
        markup_percentage = self._get_markup_percentage(flavors, toppings)
        markup_amount = subtotal * (markup_percentage / 100)

        total_cost = subtotal + markup_amount

        return {
            "cost_breakdown": {
                "flavors": flavor_costs,
                "toppings": topping_costs,
                "flavor_total": adjusted_flavor_cost,
                "topping_total": base_topping_cost,
                "preparation_cost": preparation_cost,
                "service_cost": service_cost,
                "markup_amount": markup_amount,
            },
            "subtotal": subtotal,
            "total_cost": round(total_cost, 2),
            "scoops": scoops,
            "scoop_multiplier": scoop_multiplier,
            "markup_percentage": markup_percentage,
            "cost_per_scoop": round(total_cost / scoops, 2) if scoops > 0 else 0,
        }

    def _calculate_preparation_cost(self, num_flavors: int, num_toppings: int) -> float:
        """Calculate preparation cost based on complexity."""
        # Base preparation cost
        base_prep = 0.5

        # Additional cost for multiple flavors (mixing complexity)
        flavor_complexity = max(0, (num_flavors - 1) * 0.3)

        # Additional cost for multiple toppings (assembly time)
        topping_complexity = max(0, (num_toppings - 2) * 0.2)

        return base_prep + flavor_complexity + topping_complexity

    def _get_markup_percentage(self, flavors: List[str], toppings: List[str]) -> float:
        """Calculate markup percentage based on ingredients."""
        base_markup = 15.0  # 15% base markup

        # Premium ingredients get higher markup
        premium_keywords = ["mascarpone", "espresso", "premium", "artisan", "organic"]
        premium_count = 0

        all_ingredients = flavors + toppings
        for ingredient in all_ingredients:
            ingredient_lower = ingredient.lower()
            if any(keyword in ingredient_lower for keyword in premium_keywords):
                premium_count += 1

        # Add 5% markup for each premium ingredient
        premium_markup = premium_count * 5.0

        return min(base_markup + premium_markup, 35.0)  # Cap at 35% markup

    async def validate_cost_reasonableness(
        self, total_cost: float, scoops: int, flavors: List[str], toppings: List[str]
    ) -> Dict[str, Any]:
        """Validate that calculated cost is reasonable."""
        warnings = []
        recommendations = []

        # Check cost per scoop
        cost_per_scoop = total_cost / scoops if scoops > 0 else total_cost

        if cost_per_scoop < 3.0:
            warnings.append("Cost per scoop seems unusually low")
            recommendations.append(
                "Consider increasing portion sizes or ingredient quality"
            )
        elif cost_per_scoop > 12.0:
            warnings.append("Cost per scoop is quite high")
            recommendations.append(
                "Consider optimizing ingredient selection or portions"
            )

        # Check ingredient balance
        if len(flavors) > 4:
            warnings.append("Many flavors may create confusing taste profile")
            recommendations.append("Consider limiting to 3-4 complementary flavors")

        if len(toppings) > 6:
            warnings.append("Too many toppings may overwhelm the ice cream")
            recommendations.append("Focus on 3-5 key toppings for better balance")

        # Determine overall assessment
        if len(warnings) == 0:
            assessment = "REASONABLE"
        elif len(warnings) <= 2:
            assessment = "ACCEPTABLE_WITH_NOTES"
        else:
            assessment = "NEEDS_REVIEW"

        return {
            "assessment": assessment,
            "cost_per_scoop": round(cost_per_scoop, 2),
            "warnings": warnings,
            "recommendations": recommendations,
            "is_reasonable": assessment in ["REASONABLE", "ACCEPTABLE_WITH_NOTES"],
        }

    async def calculate_bulk_discount(
        self, individual_costs: List[float], quantities: List[int]
    ) -> Dict[str, Any]:
        """Calculate bulk discounts for group orders."""
        if len(individual_costs) != len(quantities):
            raise ValueError(
                "Individual costs and quantities lists must have same length"
            )

        total_individual = sum(
            cost * qty for cost, qty in zip(individual_costs, quantities)
        )
        total_items = sum(quantities)

        # Apply bulk discount based on total items
        if total_items >= 10:
            discount_percentage = 15.0
        elif total_items >= 5:
            discount_percentage = 10.0
        elif total_items >= 3:
            discount_percentage = 5.0
        else:
            discount_percentage = 0.0

        discount_amount = total_individual * (discount_percentage / 100)
        final_total = total_individual - discount_amount

        return {
            "original_total": round(total_individual, 2),
            "discount_percentage": discount_percentage,
            "discount_amount": round(discount_amount, 2),
            "final_total": round(final_total, 2),
            "savings": round(discount_amount, 2),
            "average_per_item": round(final_total / total_items, 2)
            if total_items > 0
            else 0,
        }

    async def calculate_authoritative_cost(self, selections: List[str]) -> float:
        """Calculate authoritative cost from backend database (ignores frontend values)."""
        total_cost = 0.0

        for selection in selections:
            if selection.lower() != "skip":
                selection_costs = await self.mcp_client.get_cost_for_abstract_selection(
                    selection
                )
                total_cost += sum(selection_costs.values())

        # Add base preparation and service costs
        total_cost += 1.5  # Base costs

        # Apply basic markup
        total_cost *= 1.15  # 15% markup

        return round(total_cost, 2)
