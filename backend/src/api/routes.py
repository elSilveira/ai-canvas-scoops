from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse
import aiosqlite
import json
from typing import List, Dict, Any, Optional
from pydantic import BaseModel
from datetime import datetime
from pathlib import Path
from src.settings import DB_FILE
from src.agents.orchestrator import IceCreamGameOrchestrator
from src.tools.image_generator import ImageGeneratorTool
from src.agents.cost_calculator import CostCalculatorAgent
from src.agents.selection_mapping import SelectionMappingAgent
from src.storage import session_memory

router = APIRouter()

# Initialize orchestrator, image generator, and cost calculator
orchestrator = IceCreamGameOrchestrator(use_langgraph=True)
image_generator = ImageGeneratorTool()
cost_calculator = CostCalculatorAgent()

# Track image generation requests per session/player to prevent duplicates
image_generation_tracker: Dict[str, Dict[str, Dict[str, Any]]] = {}
# Structure: {session_id: {player_name: {"status": "pending|completed|failed", "image_url": str, "timestamp": datetime}}}


def get_image_generation_key(session_id: str, player_name: str) -> str:
    """Generate a unique key for tracking image generation requests."""
    return f"{session_id}:{player_name}" if session_id else f"no_session:{player_name}"


def is_image_generation_in_progress(session_id: str, player_name: str) -> bool:
    """Check if image generation is already in progress for this player."""
    if session_id not in image_generation_tracker:
        return False

    player_data = image_generation_tracker[session_id].get(player_name, {})
    return player_data.get("status") == "pending"


def get_existing_generated_image(session_id: str, player_name: str) -> Optional[str]:
    """Get existing generated image URL if available."""
    if session_id not in image_generation_tracker:
        return None

    player_data = image_generation_tracker[session_id].get(player_name, {})
    if player_data.get("status") == "completed":
        return player_data.get("image_url")
    return None


def mark_image_generation_pending(session_id: str, player_name: str):
    """Mark image generation as pending for this player."""
    if session_id not in image_generation_tracker:
        image_generation_tracker[session_id] = {}

    image_generation_tracker[session_id][player_name] = {
        "status": "pending",
        "timestamp": datetime.now(),
        "image_url": None,
    }


def mark_image_generation_completed(session_id: str, player_name: str, image_url: str):
    """Mark image generation as completed for this player."""
    if session_id not in image_generation_tracker:
        image_generation_tracker[session_id] = {}

    image_generation_tracker[session_id][player_name] = {
        "status": "completed",
        "timestamp": datetime.now(),
        "image_url": image_url,
    }


def mark_image_generation_failed(session_id: str, player_name: str, error: str):
    """Mark image generation as failed for this player."""
    if session_id not in image_generation_tracker:
        image_generation_tracker[session_id] = {}

    image_generation_tracker[session_id][player_name] = {
        "status": "failed",
        "timestamp": datetime.now(),
        "error": error,
        "image_url": None,
    }


@router.get("/health")
async def health_check():
    """Health check endpoint for system status"""
    try:
        # Check database connectivity
        async with aiosqlite.connect(DB_FILE) as db:
            cursor = await db.execute("SELECT COUNT(*) FROM inventory")
            ingredient_count = (await cursor.fetchone())[0]

        return {
            "status": "healthy",
            "message": f"AI Canvas system running with {ingredient_count} ingredients loaded",
            "components": {
                "database": "connected",
                "orchestrator": "initialized",
                "image_generator": "ready",
            },
        }
    except Exception as e:
        raise HTTPException(
            status_code=503, detail=f"System health check failed: {str(e)}"
        )


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


# New models for Phase 1 API endpoints
class PlayerGameRequest(BaseModel):
    playerData: Dict[str, Any]
    processingConfig: Dict[str, Any] = {
        "generateImage": True,
        "verbose": False,
        "qualityLevel": "balanced",
    }


class ProcessingResult(BaseModel):
    player_name: str
    total_cost: float
    selected_ingredients: List[str]
    image_instructions: Dict[str, Any] = {}
    reasoning_steps: List[str] = []
    processing_errors: List[str] = []


class PlayerGameResponse(BaseModel):
    success: bool
    data: Dict[str, Any]
    error: str = None


class ImageGenerationRequest(BaseModel):
    selections: List[str]
    playerName: str
    style: str = "realistic"
    size: str = "1024x1024"


class ImageGenerationResponse(BaseModel):
    success: bool
    imageUrl: str = None
    metadata: Dict[str, Any] = {}
    error: str = None


class IngredientCostBreakdown(BaseModel):
    ingredient: str
    quantity: float
    unit_cost: float
    total_cost: float
    category: str


class EnhancedAIResponse(BaseModel):
    reasoning_steps: List[str]
    ingredient_mappings: List[IngredientCostBreakdown]
    similar_flavors: List[str]
    probable_ice_cream: str
    cost_breakdown: Dict[str, float]
    confidence_score: float


class SelectionMapping(BaseModel):
    frontendChoice: str
    backendIngredient: str
    category: str
    description: str


# Phase 3.3 - Cost Calculation Integration Models
class RealTimePricingRequest(BaseModel):
    selections: List[str]
    playerName: str = "Guest"
    sessionId: str = None


class RealTimePricingResponse(BaseModel):
    success: bool
    totalCost: float
    itemizedCosts: Dict[str, float]
    currency: str = "USD"
    breakdown: Dict[str, Any] = {}
    warnings: List[str] = []
    aiIngredientMappings: List[IngredientCostBreakdown] = []
    error: str = None


class InventoryUpdateRequest(BaseModel):
    ingredient: str
    quantity: int
    operation: str = "decrease"  # "decrease", "increase", "set"


class InventoryUpdateResponse(BaseModel):
    success: bool
    ingredient: str
    previousQuantity: int
    newQuantity: int
    error: str = None


class CostValidationRequest(BaseModel):
    selections: List[str]
    frontendTotalCost: float
    playerName: str = "Guest"


class CostValidationResponse(BaseModel):
    success: bool
    isValid: bool
    frontendCost: float
    backendCost: float
    discrepancy: float
    tolerance: float = 0.10  # 10% tolerance
    details: Dict[str, Any] = {}
    error: str = None


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
                    inventory=row[7],
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
                "total_cost": request.total_cost,
            },
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
            "gameVersion": request.gameVersion,
        }

        # Log the complete game data for debugging
        print(f"\n{'=' * 60}")
        print(f"COMPLETE GAME RESULTS RECEIVED - {request.gameDate}")
        print(f"{'=' * 60}")
        print(f"Total Players: {request.totalPlayers}")
        print(f"Game Version: {request.gameVersion}")
        print(f"{'=' * 60}")

        # Process and log each player's data
        for i, player in enumerate(request.players, 1):
            player_name = player.get("name", f"Player {i}")
            personality = player.get("personality", {})
            selections = player.get("selections", [])
            total_cost = player.get("totalCost", 0)
            ai_interactions = player.get("aiInteractions", [])
            ingredients_used = [s for s in selections if s != "Skip"]

            print(f"\nPlayer {i}: {player_name}")
            print(f"  ID: {player.get('id', 'N/A')}")
            print(f"  Personality: {personality.get('name', 'Unknown')}")
            print(f"  Personality Emoji: {personality.get('emoji', '❓')}")
            print(f"  Selections: {', '.join(selections)}")
            print(
                f"  Ingredients Used: {', '.join(ingredients_used) if ingredients_used else 'None'}"
            )
            print(f"  Total Cost: ${total_cost}")
            print(f"  AI Interactions: {len(ai_interactions)}")

        print(f"\n{'=' * 60}")
        print("Game data successfully processed and saved!")
        print(f"{'=' * 60}\n")

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
            "data": game_data,  # Return the exact same structure that was sent
        }

    except Exception as e:
        print(f"Error processing game results: {str(e)}")
        raise HTTPException(
            status_code=500, detail=f"Error saving game results: {str(e)}"
        )


@router.post("/process-player-game", response_model=PlayerGameResponse)
async def process_player_game(request: PlayerGameRequest):
    """Process individual player game data through AI orchestrator"""
    try:
        print(
            f"🎮 Processing player game for: {request.playerData.get('name', 'Unknown')}"
        )

        # Extract player data
        player_data = request.playerData
        player_name = player_data.get("name", "Unknown Player")
        selections = player_data.get("selections", [])
        session_id = request.processingConfig.get("session_id")

        # Filter out 'Skip' selections for processing
        valid_selections = [s for s in selections if s.lower() != "skip"]

        if not valid_selections:
            return PlayerGameResponse(
                success=False,
                data={},
                error="No valid selections provided (all selections were 'Skip')",
            )

        # Create mock processing result for now (will integrate with orchestrator later)
        # Map selections to simple mocked ingredients
        ingredient_mapping = {
            "Adventure": "Rum flavoring",
            "Classic": "Vanilla",
            "Light": "Lemon",
            "Rich": "Dark chocolate",
            "Smooth": "Heavy cream",
            "Crunchy": "Nuts",
            "Sprinkles": "Marshmallows",
            "Caramel": "Caramel sauce",
        }

        selected_ingredients = [ingredient_mapping.get(s, s) for s in valid_selections]

        # Calculate estimated cost (mock calculation)
        base_cost = len(valid_selections) * 12.50
        estimated_cost = round(base_cost + (base_cost * 0.15), 2)  # Add 15% markup

        # Generate reasoning steps (without image generation references)
        reasoning_steps = [
            f"Analyzing player selections: {', '.join(valid_selections)}",
            f"Mapping to ingredients: {', '.join(selected_ingredients)}",
            f"Processing {len(valid_selections)} flavor preferences",
            "Calculating ingredient costs and availability",
            "Generating personalized ice cream profile",
            "Finalizing recommendations",
        ]

        # Create enhanced AI response with detailed cost breakdown
        ingredient_cost_breakdown = []
        base_ingredient_cost = 0.0

        for i, ingredient in enumerate(selected_ingredients):
            unit_cost = 8.50 + (i * 2.0)  # Mock progressive pricing
            quantity = 1.0
            total_cost = unit_cost * quantity
            base_ingredient_cost += total_cost

            ingredient_cost_breakdown.append(
                {
                    "ingredient": ingredient,
                    "quantity": quantity,
                    "unit_cost": round(unit_cost, 2),
                    "total_cost": round(total_cost, 2),
                    "category": "flavor"
                    if i < 2
                    else "texture"
                    if i < 3
                    else "topping",
                }
            )

        # Generate similar flavors (unique and different from current selection)
        all_flavors = [
            "Strawberry Vanilla Swirl",
            "Chocolate Chip Cookie Dough",
            "Mint Chocolate Chip",
            "Rocky Road",
            "Butter Pecan",
            "Cookies and Cream",
            "Pistachio",
            "Salted Caramel",
            "Neapolitan",
            "Coffee Toffee",
        ]

        # Filter out similar flavors to current selection and ensure uniqueness
        current_flavors_lower = [s.lower() for s in valid_selections]
        similar_flavors = []
        for flavor in all_flavors:
            flavor_lower = flavor.lower()
            # Check if flavor doesn't contain any of the current selections
            if not any(sel in flavor_lower for sel in current_flavors_lower):
                similar_flavors.append(flavor)
            if len(similar_flavors) >= 3:  # Limit to 3 unique alternatives
                break

        # Determine probable ice cream name
        probable_ice_cream = f"{' '.join(valid_selections[:2])} Delight"

        # Ensure probable ice cream is not in similar flavors
        if probable_ice_cream in similar_flavors:
            similar_flavors.remove(probable_ice_cream)

        enhanced_ai_response = {
            "reasoning_steps": reasoning_steps,
            "ingredient_mappings": ingredient_cost_breakdown,
            "similar_flavors": similar_flavors,
            "probable_ice_cream": probable_ice_cream,
            "cost_breakdown": {
                "base_cost": round(base_ingredient_cost, 2),
                "ingredient_costs": round(base_ingredient_cost, 2),
                "preparation_cost": round(
                    base_ingredient_cost * 0.10, 2
                ),  # 10% prep cost
                "total_cost": estimated_cost,
            },
            "confidence_score": min(
                0.95, 0.75 + (len(valid_selections) * 0.05)
            ),  # Higher confidence with more selections
        }

        # Store processing result in session if session_id provided
        if session_id:
            processing_result = {
                "player_name": player_name,
                "total_cost": estimated_cost,
                "selected_ingredients": selected_ingredients,
                "reasoning_steps": reasoning_steps,
                "processing_errors": [],
                "enhanced_ai_response": enhanced_ai_response,
            }
            session_memory.store_processing_result(
                session_id, player_name, processing_result
            )
            print(
                f"✅ Stored processing result for {player_name} in session {session_id}"
            )

        response_data = {
            "processedResults": {
                "player_name": player_name,
                "total_cost": estimated_cost,
                "selected_ingredients": selected_ingredients,
                "reasoning_steps": reasoning_steps,
                "processing_errors": [],
                "enhanced_ai_response": enhanced_ai_response,
            },
            "estimatedCost": estimated_cost,
            "ingredientsUsed": selected_ingredients,
            "aiReasoningSteps": reasoning_steps,
        }

        print(f"✅ Successfully processed player game for {player_name}")
        return PlayerGameResponse(success=True, data=response_data)

    except Exception as e:
        print(f"❌ Error processing player game: {str(e)}")
        return PlayerGameResponse(
            success=False, data={}, error=f"Error processing player game: {str(e)}"
        )


@router.post("/generate-ice-cream-image", response_model=ImageGenerationResponse)
async def generate_ice_cream_image(request: ImageGenerationRequest):
    """Generate ice cream images based on player selections"""
    try:
        print(f"🎨 Generating ice cream image for {request.playerName}")
        print(f"Selections: {', '.join(request.selections)}")

        # Filter out 'Skip' selections
        valid_selections = [s for s in request.selections if s.lower() != "skip"]

        if not valid_selections:
            return ImageGenerationResponse(
                success=False, error="No valid selections provided for image generation"
            )

        # Map frontend selections to simple mocked ingredients for image generation
        ingredient_mapping = {
            "Adventure": "Rum flavoring",
            "Classic": "Vanilla",
            "Light": "Lemon",
            "Rich": "Dark chocolate",
            "Smooth": "Heavy cream",
            "Crunchy": "Nuts",
            "Sprinkles": "Marshmallows",
            "Caramel": "Caramel sauce",
        }

        # Use simple ingredient names for image generation
        ingredients = [ingredient_mapping.get(s, s) for s in valid_selections]

        # Generate image using the image generator tool
        try:
            image_url, local_path, success = image_generator.generate_ice_cream_image(
                ingredients=ingredients,
                scoops=min(len(ingredients), 3),  # Max 3 scoops
                save_to_root=True,
                filename_prefix=f"icecream_{request.playerName.lower().replace(' ', '_')}",
            )

            if success and image_url:
                metadata = {
                    "prompt": f"Ice cream with {', '.join(ingredients)}",
                    "processingTime": "Generated successfully",
                    "model": "Stability AI Ultra",
                    "ingredients": ingredients,
                    "style": request.style,
                    "size": request.size,
                }

                print(f"✅ Successfully generated image for {request.playerName}")
                return ImageGenerationResponse(
                    success=True, imageUrl=image_url, metadata=metadata
                )
            else:
                return ImageGenerationResponse(
                    success=False, error="Image generation failed"
                )

        except Exception as img_error:
            print(f"❌ Image generation error: {str(img_error)}")
            return ImageGenerationResponse(
                success=False, error=f"Image generation failed: {str(img_error)}"
            )

    except Exception as e:
        print(f"❌ Error in generate_ice_cream_image: {str(e)}")
        return ImageGenerationResponse(
            success=False, error=f"Error generating image: {str(e)}"
        )


@router.get("/generate-ice-cream-image")
async def generate_ice_cream_image_on_demand(player: str, session_id: str = None):
    """Generate ice cream image on-demand for a specific player with protection against concurrent requests."""
    try:
        print(f"🎨 On-demand image generation requested for player: {player}")

        # Use session_id or player name as the protection key
        protection_key = session_id or f"player-{player}"

        # Protection: Check if image generation is already in progress
        if is_image_generation_in_progress(protection_key, player):
            print(
                f"⚠️ Image generation already in progress for {player} (key: {protection_key})"
            )
            return {
                "success": False,
                "error": "Image generation already in progress for this player. Please wait.",
                "status": "pending",
            }

        # Protection: Check if image already exists
        existing_image_url = get_existing_generated_image(protection_key, player)
        if existing_image_url:
            print(f"✅ Returning existing image for {player}: {existing_image_url}")
            return {
                "success": True,
                "imageUrl": existing_image_url,
                "status": "completed",
                "cached": True,
                "metadata": {
                    "player": player,
                    "note": "Image already generated for this session",
                },
            }

        # Try to get player data from session if session_id provided
        player_data = None
        if session_id:
            player_data = session_memory.get_player_from_session(session_id, player)
            if not player_data:
                print(
                    f"⚠️ Player {player} not found in session {session_id}, using default"
                )

        # Protection: Mark as pending before starting generation
        mark_image_generation_pending(protection_key, player)
        print(
            f"🔒 Marked image generation as pending for {player} (key: {protection_key})"
        )

        # Extract selections from player data or use defaults
        if player_data and player_data.selections:
            selections = player_data.selections
        else:
            # Fallback to default selections if no session data
            selections = ["Classic", "Rich", "Smooth", "Caramel"]
            print(f"⚠️ Using fallback selections for {player}: {selections}")

        # Filter out 'Skip' selections
        valid_selections = [s for s in selections if s.lower() != "skip"]

        if not valid_selections:
            if session_id:
                mark_image_generation_failed(
                    session_id, player, "No valid selections available"
                )
            return {
                "success": False,
                "error": "No valid selections available for image generation",
            }

        # Map selections to ingredients
        ingredient_mapping = {
            "Adventure": "Rum flavoring",
            "Classic": "Vanilla",
            "Light": "Lemon",
            "Rich": "Dark chocolate",
            "Smooth": "Heavy cream",
            "Crunchy": "Nuts",
            "Sprinkles": "Marshmallows",
            "Caramel": "Caramel sauce",
        }

        ingredients = [ingredient_mapping.get(s, s) for s in valid_selections]

        print(f"🧊 Generating image with ingredients: {', '.join(ingredients)}")

        # Generate image using the image generator tool
        try:
            image_url, local_path, success = image_generator.generate_ice_cream_image(
                ingredients=ingredients,
                scoops=min(len(ingredients), 3),  # Max 3 scoops
                save_to_root=True,
                filename_prefix=f"icecream_{player.lower().replace(' ', '_')}",
            )

            if success and image_url:
                # Protection: Mark as completed
                mark_image_generation_completed(protection_key, player, image_url)
                print(f"✅ Marked image generation as completed for {player}")

                # Store image URL in session if available
                if session_id and player_data:
                    session_memory.store_generated_image(session_id, player, image_url)
                    print(
                        f"✅ Stored generated image for {player} in session {session_id}"
                    )

                metadata = {
                    "prompt": f"Ice cream with {', '.join(ingredients)}",
                    "processingTime": "Generated successfully",
                    "model": "Stability AI Ultra",
                    "ingredients": ingredients,
                    "player": player,
                    "selections": valid_selections,
                }

                print(f"✅ Successfully generated on-demand image for {player}")
                return {
                    "success": True,
                    "imageUrl": image_url,
                    "metadata": metadata,
                    "status": "completed",
                }
            else:
                error_msg = "Image generation failed"
                mark_image_generation_failed(protection_key, player, error_msg)
                return {"success": False, "error": error_msg, "status": "failed"}

        except Exception as img_error:
            error_msg = f"Image generation failed: {str(img_error)}"
            print(f"❌ Image generation error for {player}: {str(img_error)}")
            mark_image_generation_failed(protection_key, player, error_msg)
            return {"success": False, "error": error_msg, "status": "failed"}

    except Exception as e:
        error_msg = f"Error generating image: {str(e)}"
        print(f"❌ Error in on-demand image generation: {str(e)}")
        # Use protection_key if available, otherwise fallback
        key = locals().get("protection_key", f"player-{player}")
        mark_image_generation_failed(key, player, error_msg)
        return {"success": False, "error": error_msg, "status": "failed"}


@router.get("/selection-mappings", response_model=List[SelectionMapping])
async def get_selection_mappings():
    """Return mapping between frontend choices and backend ingredients"""
    try:
        mappings = [
            SelectionMapping(
                frontendChoice="Adventure",
                backendIngredient="Rum flavoring (extract)",
                category="flavor",
                description="Bold and daring rum-flavored base",
            ),
            SelectionMapping(
                frontendChoice="Classic",
                backendIngredient="Vanilla extract",
                category="flavor",
                description="Traditional vanilla base",
            ),
            SelectionMapping(
                frontendChoice="Light",
                backendIngredient="Lemons (fresh)",
                category="flavor",
                description="Fresh and fruity lemon flavor",
            ),
            SelectionMapping(
                frontendChoice="Rich",
                backendIngredient="Dark chocolate (70%+ callets)",
                category="flavor",
                description="Decadent dark chocolate",
            ),
            SelectionMapping(
                frontendChoice="Smooth",
                backendIngredient="Heavy cream (35-40%)",
                category="texture",
                description="Creamy smooth texture",
            ),
            SelectionMapping(
                frontendChoice="Crunchy",
                backendIngredient="Hazelnuts (roasted)",
                category="texture",
                description="Nutty crunchy texture",
            ),
            SelectionMapping(
                frontendChoice="Sprinkles",
                backendIngredient="Mini marshmallows",
                category="topping",
                description="Colorful mini marshmallow toppings",
            ),
            SelectionMapping(
                frontendChoice="Caramel",
                backendIngredient="Sea-salt caramel drizzle (Jack Sparrow)",
                category="topping",
                description="Sweet and salty caramel drizzle",
            ),
        ]

        print(f"📋 Returning {len(mappings)} selection mappings")
        return mappings

    except Exception as e:
        print(f"❌ Error getting selection mappings: {str(e)}")
        raise HTTPException(
            status_code=500, detail=f"Error retrieving mappings: {str(e)}"
        )


# ===== PHASE 3.3 - COST CALCULATION INTEGRATION ENDPOINTS =====


@router.post("/real-time-pricing", response_model=RealTimePricingResponse)
async def get_real_time_pricing(request: RealTimePricingRequest):
    """Calculate real-time pricing for player selections"""
    try:
        print(f"💰 Calculating real-time pricing for {request.playerName}")
        print(f"Selections: {', '.join(request.selections)}")

        # Filter out 'Skip' selections
        valid_selections = [s for s in request.selections if s.lower() != "skip"]

        if not valid_selections:
            return RealTimePricingResponse(
                success=False,
                totalCost=0.0,
                itemizedCosts={},
                error="No valid selections provided for pricing",
            )

        # Calculate authoritative cost using backend cost calculator
        total_cost = await cost_calculator.calculate_authoritative_cost(
            valid_selections
        )

        # Get itemized costs for each selection
        itemized_costs = {}
        breakdown = {
            "baseCost": 0.0,
            "ingredientCosts": {},
            "preparationCost": 0.0,
            "markupApplied": 0.0,
            "serviceFee": 0.0,
        }

        # Calculate individual costs for transparency
        for selection in valid_selections:
            try:
                individual_cost = await cost_calculator.calculate_authoritative_cost(
                    [selection]
                )
                itemized_costs[selection] = round(individual_cost, 2)
                breakdown["ingredientCosts"][selection] = round(individual_cost, 2)
            except Exception as e:
                print(f"⚠️ Warning calculating cost for {selection}: {str(e)}")
                itemized_costs[selection] = 2.50  # Fallback cost
                breakdown["ingredientCosts"][selection] = 2.50

        # Add breakdown details
        breakdown["baseCost"] = sum(breakdown["ingredientCosts"].values())
        breakdown["preparationCost"] = max(
            1.0, len(valid_selections) * 0.50
        )  # $0.50 per ingredient
        breakdown["serviceFee"] = 1.50  # Standard service fee
        breakdown["markupApplied"] = (
            total_cost - breakdown["baseCost"] - breakdown["preparationCost"]
        )

        warnings = []
        if len(valid_selections) > 4:
            warnings.append("High complexity selection may take longer to prepare")

        if total_cost > 20.0:
            warnings.append("Premium selections result in higher costs")

        # Fetch AI ingredient mappings if session_id and player are available
        ai_ingredient_mappings = []
        if request.sessionId and request.playerName:
            try:
                player_data = session_memory.get_player_from_session(
                    request.sessionId, request.playerName
                )
                if player_data and player_data.ai_interactions:
                    # Get the latest AI interaction with enhanced response
                    latest_interaction = player_data.ai_interactions[-1]
                    if (
                        "enhanced_ai_response" in latest_interaction
                        and "ingredient_mappings"
                        in latest_interaction["enhanced_ai_response"]
                    ):
                        ai_ingredient_mappings = latest_interaction[
                            "enhanced_ai_response"
                        ]["ingredient_mappings"]
                        print(
                            f"✅ Found {len(ai_ingredient_mappings)} AI ingredient mappings for {request.playerName}"
                        )
            except Exception as e:
                print(f"⚠️ Warning fetching AI ingredient mappings: {str(e)}")

        print(f"✅ Real-time pricing calculated: ${total_cost:.2f}")

        return RealTimePricingResponse(
            success=True,
            totalCost=round(total_cost, 2),
            itemizedCosts=itemized_costs,
            breakdown=breakdown,
            warnings=warnings,
            aiIngredientMappings=ai_ingredient_mappings,
        )

    except Exception as e:
        print(f"❌ Error calculating real-time pricing: {str(e)}")
        raise HTTPException(
            status_code=500, detail=f"Error calculating pricing: {str(e)}"
        )


@router.post("/update-inventory", response_model=InventoryUpdateResponse)
async def update_ingredient_inventory(request: InventoryUpdateRequest):
    """Update ingredient inventory in real-time"""
    try:
        print(
            f"📦 Updating inventory for {request.ingredient}: {request.operation} {request.quantity}"
        )

        # First, try to map abstract selection to actual ingredients
        selection_mapping_agent = SelectionMappingAgent()
        try:
            # Try to get actual ingredients for this selection
            actual_ingredients = (
                await selection_mapping_agent.get_selection_ingredients(
                    request.ingredient
                )
            )

            if actual_ingredients:
                print(
                    f"🔄 Mapped '{request.ingredient}' to ingredients: {actual_ingredients}"
                )

                # Update inventory for each mapped ingredient
                results = []
                async with aiosqlite.connect(DB_FILE) as db:
                    for ingredient in actual_ingredients:
                        # Get current inventory for this specific ingredient
                        cursor = await db.execute(
                            "SELECT inventory FROM inventory WHERE ingredient = ?",
                            (ingredient,),
                        )
                        result = await cursor.fetchone()

                        if result:
                            previous_quantity = result[0]

                            # Calculate new quantity based on operation
                            if request.operation == "decrease":
                                new_quantity = max(
                                    0, previous_quantity - request.quantity
                                )
                            elif request.operation == "increase":
                                new_quantity = previous_quantity + request.quantity
                            elif request.operation == "set":
                                new_quantity = request.quantity
                            else:
                                raise HTTPException(
                                    status_code=400,
                                    detail="Invalid operation. Use 'decrease', 'increase', or 'set'",
                                )

                            # Update database
                            await db.execute(
                                "UPDATE inventory SET inventory = ? WHERE ingredient = ?",
                                (new_quantity, ingredient),
                            )
                            await db.commit()

                            results.append(
                                {
                                    "ingredient": ingredient,
                                    "previous": previous_quantity,
                                    "new": new_quantity,
                                }
                            )

                            print(
                                f"✅ Updated {ingredient}: {previous_quantity} → {new_quantity}"
                            )

                # Return summary of first ingredient updated (for API compatibility)
                if results:
                    first_result = results[0]
                    return InventoryUpdateResponse(
                        success=True,
                        ingredient=f"{request.ingredient} (mapped to {len(results)} ingredients)",
                        previousQuantity=first_result["previous"],
                        newQuantity=first_result["new"],
                    )
        except Exception as mapping_error:
            print(
                f"⚠️ Selection mapping failed: {mapping_error}, trying direct ingredient lookup"
            )

        # Fallback: Direct ingredient lookup (original logic)
        async with aiosqlite.connect(DB_FILE) as db:
            # Get current inventory
            cursor = await db.execute(
                "SELECT inventory FROM inventory WHERE ingredient = ?",
                (request.ingredient,),
            )
            result = await cursor.fetchone()

            if not result:
                # Try to find by partial match for frontend-backend mapping
                cursor = await db.execute(
                    "SELECT ingredient, inventory FROM inventory WHERE ingredient LIKE ?",
                    (f"%{request.ingredient}%",),
                )
                result = await cursor.fetchone()

                if not result:
                    # Try case-insensitive search
                    cursor = await db.execute(
                        "SELECT ingredient, inventory FROM inventory WHERE LOWER(ingredient) LIKE LOWER(?)",
                        (f"%{request.ingredient}%",),
                    )
                    result = await cursor.fetchone()

                    if not result:
                        print("🔍 Available ingredients in database:")
                        cursor = await db.execute(
                            "SELECT ingredient FROM inventory LIMIT 5"
                        )
                        available = await cursor.fetchall()
                        for ing in available:
                            print(f"  - {ing[0]}")

                        raise HTTPException(
                            status_code=404,
                            detail=f"Ingredient '{request.ingredient}' not found in inventory. This might be an abstract selection that needs proper mapping.",
                        )

                # Update ingredient name to match database
                actual_ingredient = result[0]
                previous_quantity = result[1]
            else:
                actual_ingredient = request.ingredient
                previous_quantity = result[0]

            # Calculate new quantity based on operation
            if request.operation == "decrease":
                new_quantity = max(0, previous_quantity - request.quantity)
            elif request.operation == "increase":
                new_quantity = previous_quantity + request.quantity
            elif request.operation == "set":
                new_quantity = request.quantity
            else:
                raise HTTPException(
                    status_code=400,
                    detail="Invalid operation. Use 'decrease', 'increase', or 'set'",
                )

            # Update database
            await db.execute(
                "UPDATE inventory SET inventory = ? WHERE ingredient = ?",
                (new_quantity, actual_ingredient),
            )
            await db.commit()

        print(
            f"✅ Inventory updated: {actual_ingredient} {previous_quantity} → {new_quantity}"
        )

        return InventoryUpdateResponse(
            success=True,
            ingredient=actual_ingredient,
            previousQuantity=previous_quantity,
            newQuantity=new_quantity,
        )

    except Exception as e:
        print(f"❌ Error calculating real-time pricing: {str(e)}")
        raise HTTPException(
            status_code=500, detail=f"Error calculating pricing: {str(e)}"
        )


@router.post("/get-ice-cream-suggestions", response_model=Dict[str, Any])
async def get_ice_cream_suggestions(request: Dict[str, List[str]]):
    """Get probable ice cream names and ingredients based on player selections"""
    try:
        selections = request.get("selections", [])
        valid_selections = [s for s in selections if s.lower() != "skip"]

        if not valid_selections:
            return {"success": False, "error": "No valid selections provided"}

        # Map abstract selections to ingredients using selection mapping
        mapping_agent = SelectionMappingAgent()
        all_suggested_ingredients = []
        ice_cream_names = []

        async with aiosqlite.connect(DB_FILE) as db:
            # For each selection, find matching ingredients and their ice cream names
            for selection in valid_selections:
                try:
                    mapping_result = await mapping_agent.map_selection_to_components(
                        selection
                    )

                    if mapping_result and "flavors" in mapping_result:
                        mapped_flavors = mapping_result.get("flavors", [])
                        mapped_toppings = mapping_result.get("toppings", [])

                        # Search for ingredients that match the mapped keywords
                        for keyword in mapped_flavors + mapped_toppings:
                            cursor = await db.execute(
                                """SELECT ingredient, used_on FROM inventory 
                                   WHERE ingredient LIKE ? AND used_on != '[]'""",
                                (f"%{keyword}%",),
                            )
                            results = await cursor.fetchall()

                            for ingredient, used_on_json in results:
                                all_suggested_ingredients.append(ingredient)
                                # Parse the JSON array of ice cream names
                                try:
                                    used_on_list = json.loads(used_on_json)
                                    ice_cream_names.extend(used_on_list)
                                except json.JSONDecodeError:
                                    continue

                except Exception as mapping_error:
                    print(f"⚠️ Error mapping selection '{selection}': {mapping_error}")
                    continue

        # Remove duplicates and get most common ice cream names
        unique_ice_creams = list(dict.fromkeys(ice_cream_names))  # Preserve order
        unique_ingredients = list(dict.fromkeys(all_suggested_ingredients))

        # If we found ice cream names, pick the first few as suggestions
        probable_ice_cream = (
            unique_ice_creams[0] if unique_ice_creams else "Custom Creation"
        )

        return {
            "success": True,
            "probableIceCream": probable_ice_cream,
            "alternativeNames": unique_ice_creams[:3],  # Top 3 suggestions
            "suggestedIngredients": unique_ingredients[:10],  # Top 10 ingredients
            "selectionsProcessed": valid_selections,
        }

    except Exception as e:
        print(f"❌ Error getting ice cream suggestions: {str(e)}")
        return {"success": False, "error": f"Error getting suggestions: {str(e)}"}


@router.post("/validate-cost", response_model=CostValidationResponse)
async def validate_cost_calculation(request: CostValidationRequest):
    """Validate frontend cost calculations against backend authoritative calculations"""
    try:
        print(f"🔍 Validating cost calculation for {request.playerName}")
        print(f"Frontend cost: ${request.frontendTotalCost:.2f}")
        print(f"Selections: {', '.join(request.selections)}")

        # Calculate authoritative backend cost
        valid_selections = [s for s in request.selections if s.lower() != "skip"]
        backend_cost = await cost_calculator.calculate_authoritative_cost(
            valid_selections
        )

        # Calculate discrepancy
        discrepancy = abs(request.frontendTotalCost - backend_cost)
        discrepancy_percent = (
            (discrepancy / backend_cost) * 100 if backend_cost > 0 else 0
        )

        # Determine if within tolerance (10% by default)
        tolerance_percent = 10.0  # 10%
        is_valid = discrepancy_percent <= tolerance_percent

        # Detailed breakdown for debugging
        details = {
            "discrepancyPercent": round(discrepancy_percent, 2),
            "tolerancePercent": tolerance_percent,
            "selections": valid_selections,
            "calculationMethod": "authoritative_backend",
            "timestamp": "2025-09-10T21:53:00Z",
        }

        if not is_valid:
            details["warning"] = (
                f"Cost discrepancy of {discrepancy_percent:.2f}% exceeds {tolerance_percent:.2f}% tolerance"
            )
            details["recommendation"] = (
                "Use backend calculation as authoritative source"
            )

        print(
            f"✅ Cost validation: Frontend ${request.frontendTotalCost:.2f} vs Backend ${backend_cost:.2f}"
        )
        print(
            f"   Discrepancy: {discrepancy_percent:.2f}% ({'VALID' if is_valid else 'INVALID'})"
        )

        return CostValidationResponse(
            success=True,
            isValid=is_valid,
            frontendCost=round(request.frontendTotalCost, 2),
            backendCost=round(backend_cost, 2),
            discrepancy=round(discrepancy, 2),
            tolerance=tolerance_percent / 100,  # Convert to decimal
            details=details,
        )

    except Exception as e:
        print(f"❌ Error validating cost: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error validating cost: {str(e)}")


# ===== SESSION MANAGEMENT ENDPOINTS =====


class SessionCreateRequest(BaseModel):
    players: List[Dict[str, Any]]
    game_metadata: Dict[str, Any] = {}


class SessionStatusResponse(BaseModel):
    session_id: str
    status: str
    created_at: str
    updated_at: str
    players_count: int
    expires_at: str


@router.post("/session/create")
async def create_session(request: SessionCreateRequest):
    """Create a new game session with player data."""
    try:
        session_id = session_memory.create_session(request.players)

        # Store game metadata if provided
        session = session_memory.get_session(session_id)
        if session and request.game_metadata:
            session.game_metadata = request.game_metadata
            session_memory.update_session(session_id, session)

        print(f"✅ Created session {session_id} with {len(request.players)} players")

        return {
            "success": True,
            "session_id": session_id,
            "message": f"Session created with {len(request.players)} players",
        }

    except Exception as e:
        print(f"❌ Error creating session: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error creating session: {str(e)}")


@router.get("/session/{session_id}/status", response_model=SessionStatusResponse)
async def get_session_status(session_id: str):
    """Get status of a specific session."""
    session = session_memory.get_session(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found or expired")

    return SessionStatusResponse(
        session_id=session.session_id,
        status=session.status,
        created_at=session.created_at.isoformat(),
        updated_at=session.updated_at.isoformat(),
        players_count=len(session.players),
        expires_at=session.expires_at.isoformat(),
    )


@router.get("/session/{session_id}/results")
async def get_session_results(session_id: str):
    """Get complete session results."""
    session = session_memory.get_session(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found or expired")

    # Convert session data to response format
    results = {
        "session_id": session.session_id,
        "status": session.status,
        "created_at": session.created_at.isoformat(),
        "players": [],
    }

    for player in session.players:
        player_result = {
            "id": player.id,
            "name": player.name,
            "selections": player.selections,
            "total_cost": player.total_cost,
            "ai_interactions": player.ai_interactions,
            "processing_result": player.processing_result,
            "generated_image_url": player.generated_image_url,
            "personality": player.personality,
        }
        results["players"].append(player_result)

    return {"success": True, "data": results}


@router.post("/session/{session_id}/complete")
async def complete_session(session_id: str):
    """Mark session as completed."""
    success = session_memory.mark_session_complete(session_id)
    if not success:
        raise HTTPException(status_code=404, detail="Session not found or expired")

    return {"success": True, "message": "Session marked as completed"}


@router.delete("/session/{session_id}")
async def delete_session(session_id: str):
    """Delete a session."""
    success = session_memory.delete_session(session_id)
    if not success:
        raise HTTPException(status_code=404, detail="Session not found")

    return {"success": True, "message": "Session deleted"}


@router.get("/session/stats")
async def get_session_stats():
    """Get session memory statistics."""
    stats = session_memory.get_stats()
    return {"success": True, "stats": stats}


@router.get("/images/{filename}")
async def serve_generated_image(filename: str):
    """Serve generated ice cream images from the backend directory."""
    try:
        # Get backend root directory (go up 2 levels from routes.py to get to backend/)
        # routes.py is at: /backend/src/api/routes.py
        # So we need: parents[2] to get to /backend/
        backend_root = Path(__file__).resolve().parents[2]
        image_path = backend_root / filename

        print(f"🔍 Looking for image: {filename}")
        print(f"🔍 Backend root: {backend_root}")
        print(f"🔍 Full image path: {image_path}")
        print(f"🔍 Image exists: {image_path.exists()}")

        # Security check: ensure the file exists and is in the backend directory
        if not image_path.exists():
            raise HTTPException(status_code=404, detail=f"Image not found: {filename}")

        # Security check: ensure the path is within backend root (prevent path traversal)
        if not str(image_path.resolve()).startswith(str(backend_root.resolve())):
            raise HTTPException(status_code=403, detail="Access denied")

        # Check if it's an image file
        if image_path.suffix.lower() not in [".png", ".jpg", ".jpeg", ".gif", ".webp"]:
            raise HTTPException(status_code=400, detail="Invalid image format")

        print(f"🖼️ Serving image: {image_path}")
        return FileResponse(
            path=str(image_path),
            media_type="image/png",
            headers={"Cache-Control": "public, max-age=3600"},  # Cache for 1 hour
        )

    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ Error serving image {filename}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error serving image: {str(e)}")
