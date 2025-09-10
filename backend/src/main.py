import asyncio
from src.mcp.server import start_mcp


async def main():
    await start_mcp()


if __name__ == "__main__":
    asyncio.run(main())
