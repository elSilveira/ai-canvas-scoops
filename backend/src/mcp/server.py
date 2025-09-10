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


async def start_mcp():
    await init_db()
    await mcp.run_http_async(
        transport="streamable-http",
        host="127.0.0.1",
        port=8001,
    )
