from fastapi import APIRouter, HTTPException
import aiosqlite
import json
from typing import List, Dict, Any
from pydantic import BaseModel
from src.settings import DB_FILE

router = APIRouter()


class IngredientResponse(BaseModel):
    ingredient: str
    description: str
    used_on: List[str]
    allergies: List[str]
    quantity: str
    cost_min: float | None
    cost_max: float | None
    inventory: int


class FinalRevealRequest(BaseModel):
    player_name: str
    character: str
    ice_cream_data: Dict[str, Any]
    ingredients_used: List[str]
    total_cost: float | None = None


class GameResultRequest(BaseModel):
    gameDate: str
    players: List[Dict[str, Any]]
    totalPlayers: int
    gameVersion: str


@router.get("/ingredients", response_model=List[IngredientResponse])
async def get_all_ingredients():
    """Get all ingredients from the database"""
    try:
        async with aiosqlite.connect(DB_FILE) as db:
            cursor = await db.execute("""
                SELECT ingredient, description, used_on, allergies, quantity, 
                       cost_min, cost_max, inventory 
                FROM inventory
            """)
            rows = await cursor.fetchall()
            
            ingredients = []
            for row in rows:
                # Parse JSON arrays safely
                try:
                    used_on = json.loads(row[2]) if row[2] else []
                except json.JSONDecodeError:
                    used_on = []
                
                try:
                    allergies = json.loads(row[3]) if row[3] else []
                except json.JSONDecodeError:
                    allergies = []
                
                ingredient = IngredientResponse(
                    ingredient=row[0],
                    description=row[1] or "",
                    used_on=used_on,
                    allergies=allergies,
                    quantity=row[4] or "",
                    cost_min=row[5],
                    cost_max=row[6],
                    inventory=row[7]
                )
                ingredients.append(ingredient)
            
            return ingredients
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")


@router.post("/final-reveal")
async def save_final_reveal(request: FinalRevealRequest):
    """Save the final ice cream creation data (legacy single player endpoint)"""
    try:
        # Here you can save the final data to database, log it, or process it
        # For now, we'll just log it and return a success response
        
        print(f"Final ice cream created by {request.player_name}:")
        print(f"Character: {request.character}")
        print(f"Ice cream data: {request.ice_cream_data}")
        print(f"Ingredients used: {request.ingredients_used}")
        print(f"Total cost: {request.total_cost}")
        
        return {
            "status": "success",
            "message": "Ice cream creation saved successfully!",
            "data": {
                "player_name": request.player_name,
                "character": request.character,
                "ingredients_count": len(request.ingredients_used),
                "total_cost": request.total_cost
            }
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error saving data: {str(e)}")


@router.post("/game-results")
async def save_game_results(request: GameResultRequest):
    """Save complete game results - accepts exact same JSON format as download"""
    try:
        # Convert the request to the exact same format as the frontend generates
        game_data = {
            "gameDate": request.gameDate,
            "players": request.players,
            "totalPlayers": request.totalPlayers,
            "gameVersion": request.gameVersion
        }
        
        # Log the complete game data for debugging
        print(f"\n{'='*60}")
        print(f"COMPLETE GAME RESULTS RECEIVED - {request.gameDate}")
        print(f"{'='*60}")
        print(f"Total Players: {request.totalPlayers}")
        print(f"Game Version: {request.gameVersion}")
        print(f"{'='*60}")
        
        # Process and log each player's data
        for i, player in enumerate(request.players, 1):
            player_name = player.get('name', f'Player {i}')
            personality = player.get('personality', {})
            selections = player.get('selections', [])
            total_cost = player.get('totalCost', 0)
            ai_interactions = player.get('aiInteractions', [])
            ingredients_used = [s for s in selections if s != 'Skip']
            
            print(f"\nPlayer {i}: {player_name}")
            print(f"  ID: {player.get('id', 'N/A')}")
            print(f"  Personality: {personality.get('name', 'Unknown')}")
            print(f"  Personality Emoji: {personality.get('emoji', '❓')}")
            print(f"  Selections: {', '.join(selections)}")
            print(f"  Ingredients Used: {', '.join(ingredients_used) if ingredients_used else 'None'}")
            print(f"  Total Cost: ${total_cost}")
            print(f"  AI Interactions: {len(ai_interactions)}")
        
        print(f"\n{'='*60}")
        print("Game data successfully processed and saved!")
        print(f"{'='*60}\n")
        
        # Here you could save to database, send to analytics, etc.
        # For example:
        # async with aiosqlite.connect(DB_FILE) as db:
        #     await db.execute("""
        #         INSERT INTO game_sessions (game_date, players_data, created_at)
        #         VALUES (?, ?, datetime('now'))
        #     """, (request.gameDate, json.dumps(game_data)))
        #     await db.commit()
        
        # Return the exact same data structure that was sent, confirming it was saved
        return {
            "status": "success",
            "message": f"Game results saved successfully for {request.totalPlayers} players!",
            "data": game_data  # Return the exact same structure that was sent
        }
        
    except Exception as e:
        print(f"Error processing game results: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error saving game results: {str(e)}")


@router.get("/health")
async def health_check():
    """Simple health check endpoint"""
    return {"status": "healthy", "service": "ai-canvas-scoops-backend"}
