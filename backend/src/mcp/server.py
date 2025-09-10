import aiosqlite

from fastmcp import FastMCP
from src.database.load_database import init_db
from src.settings import DB_FILE

mcp = FastMCP("inventory_db")


@mcp.tool()
async def list_ingredients():
    async with aiosqlite.connect(DB_FILE) as db:
        cursor = await db.execute("SELECT ingredient FROM inventory")
        rows = await cursor.fetchall()
        return [row[0] for row in rows]


@mcp.tool()
async def get_ingredient(ingredient_name: str):
    async with aiosqlite.connect(DB_FILE) as db:
        cursor = await db.execute(
            "SELECT * FROM inventory WHERE ingredient = ?", (ingredient_name,)
        )
        row = await cursor.fetchone()
        if row:
            columns = [column[0] for column in cursor.description]
            return dict(zip(columns, row))
        return None


@mcp.tool()
async def get_ingredient_info(ingredient_name: str):
    async with aiosqlite.connect(DB_FILE) as db:
        cursor = await db.execute(
            "SELECT * FROM inventory WHERE ingredient = ?", (ingredient_name,)
        )
        row = await cursor.fetchone()
        if row:
            return row[0]
        return None


@mcp.tool()
async def get_icecream_flavours():
    async with aiosqlite.connect(DB_FILE) as db:
        cursor = await db.execute("SELECT used_on FROM inventory WHERE used_on != '[]'")
        rows = await cursor.fetchall()
        flavours = [row[0][1:-1].split(", ") for row in rows]
        unique_flavours = set(
            flavour.strip('"') for sublist in flavours for flavour in sublist
        )
        return list(unique_flavours)


@mcp.tool()
async def decrease_inventory(ingredient_name: str, amount: int):
    async with aiosqlite.connect(DB_FILE) as db:
        await db.execute(
            "UPDATE inventory SET inventory = inventory - ? WHERE ingredient = ? AND inventory >= ?",
            (amount, ingredient_name, amount),
        )
        await db.commit()


@mcp.tool()
async def get_ingredient_cost(ingredient_name: str):
    async with aiosqlite.connect(DB_FILE) as db:
        cursor = await db.execute(
            "SELECT cost_min, cost_max FROM inventory WHERE ingredient = ?",
            (ingredient_name,),
        )
        row = await cursor.fetchone()
        if row:
            return {"cost_min": row[0], "cost_max": row[1]}
        return None


@mcp.tool()
async def get_ingredient_description(ingredient_name: str):
    async with aiosqlite.connect(DB_FILE) as db:
        cursor = await db.execute(
            "SELECT description FROM inventory WHERE ingredient = ?", (ingredient_name,)
        )
        row = await cursor.fetchone()
        if row:
            return row[0]
        return None


@mcp.tool()
async def get_ingredient_allergies(ingredient_name: str):
    async with aiosqlite.connect(DB_FILE) as db:
        cursor = await db.execute(
            "SELECT allergies FROM inventory WHERE ingredient = ?", (ingredient_name,)
        )
        row = await cursor.fetchone()
        if row:
            return row[0]
        return None


class MCPServerClient:
    """Client wrapper for MCP server tools used by ReAct agents."""

    async def map_selection_to_ingredients(self, selection: str) -> list[str]:
        """Map abstract selection to concrete ingredients."""
        # Mock implementation for ReAct demonstration
        ingredient_map = {
            "Rich": ["dark_chocolate", "mascarpone", "caramel_sauce"],
            "Crunchy": ["chocolate_chips", "crushed_nuts", "cookie_crumbles"],
            "Sweet": ["vanilla_ice_cream", "strawberry_sauce", "whipped_cream"],
            "Fruity": ["strawberry_ice_cream", "blueberries", "raspberry_sauce"],
        }
        return ingredient_map.get(selection, ["vanilla_ice_cream"])

    async def get_ingredient_cost(self, ingredient: str) -> float:
        """Get cost for a specific ingredient."""
        # Mock costs for ReAct demonstration
        costs = {
            "dark_chocolate": 0.50,
            "mascarpone": 0.48,
            "caramel_sauce": 0.35,
            "chocolate_chips": 0.25,
            "crushed_nuts": 0.40,
            "cookie_crumbles": 0.30,
            "vanilla_ice_cream": 0.20,
            "strawberry_sauce": 0.15,
            "whipped_cream": 0.18,
            "strawberry_ice_cream": 0.22,
            "blueberries": 0.60,
            "raspberry_sauce": 0.25,
        }
        return costs.get(ingredient, 0.10)

    async def get_cost_for_abstract_selection(self, selection: str) -> dict[str, float]:
        """Get costs for all ingredients in an abstract selection."""
        ingredients = await self.map_selection_to_ingredients(selection)
        costs = {}
        for ingredient in ingredients:
            costs[ingredient] = await self.get_ingredient_cost(ingredient)
        return costs

    async def generate_ice_cream_image(self, prompt: str) -> str:
        """Generate image for ice cream (mock implementation)."""
        # Mock image URL for ReAct demonstration
        return f"https://example.com/generated_ice_cream_image.jpg?prompt={prompt[:50]}"


async def start_mcp():
    await init_db()
    await mcp.run_http_async(
        transport="streamable-http",
        host="127.0.0.1",
        port=8001,
    )
