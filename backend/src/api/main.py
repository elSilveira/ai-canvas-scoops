"""
FastAPI Integration for AI Canvas Scoops - Phase 3 Implementation
Main API endpoints for game-based ice cream processing.
"""

import json
from datetime import datetime
from typing import Dict, Any, Optional
from fastapi import FastAPI, UploadFile, File, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from src.agents.orchestrator import IceCreamGameOrchestrator
from src.models.game_data import GameData, PlayerData
from src.models.processing_result import ProcessingResult, GameProcessingResult


class APIResponse(BaseModel):
    """Standard API response format."""

    success: bool
    data: Optional[Any] = None
    error: Optional[str] = None
    debug_info: Optional[Dict[str, Any]] = None
    timestamp: datetime = datetime.now()


class ProcessingConfig(BaseModel):
    """Configuration for processing requests."""

    skip_personality: bool = False
    verbose_logging: bool = False
    use_langgraph: bool = True
    generate_debug_report: bool = False
    thread_id: Optional[str] = None


class CostValidationRequest(BaseModel):
    """Request for cost validation only."""

    game_data: GameData
    compare_with_frontend: bool = True


# Initialize FastAPI app
app = FastAPI(
    title="AI Canvas Scoops API",
    description="LLM Adapter API for game-based ice cream processing with ReAct framework",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize orchestrator
orchestrator = IceCreamGameOrchestrator(use_langgraph=True)

# In-memory storage for debug reports (replace with proper storage in production)
debug_reports: Dict[str, Dict[str, Any]] = {}


@app.get("/", response_model=APIResponse)
async def root():
    """Root endpoint with API information."""
    return APIResponse(
        success=True,
        data={
            "service": "AI Canvas Scoops API",
            "version": "1.0.0",
            "features": [
                "Game-based ice cream processing",
                "ReAct framework implementation",
                "LangGraph workflow orchestration",
                "Authoritative backend cost calculation",
                "Personality-driven enhancements",
                "Complete reasoning traceability",
            ],
            "endpoints": {
                "process_game": "/api/process-game-results",
                "process_player": "/api/process-single-player",
                "validate_costs": "/api/validate-game-costs",
                "debug_report": "/api/debug-report/{session_id}",
                "mappings": "/api/selection-mappings",
            },
        },
    )


@app.post("/api/process-game-results", response_model=APIResponse)
async def process_game_results(
    game_data: GameData,
    config: ProcessingConfig = ProcessingConfig(),
    background_tasks: BackgroundTasks = None,
):
    """
    Main endpoint: receives game results and returns processed ice cream data for all players.

    This is the primary LLM adapter endpoint that:
    1. Processes game-based selections using ReAct framework
    2. Calculates authoritative costs from backend database
    3. Generates image instructions with personality influence
    4. Provides complete reasoning traces for debugging
    """
    try:
        start_time = datetime.now()

        # Generate thread ID if not provided
        thread_id = config.thread_id or f"game_{start_time.strftime('%Y%m%d_%H%M%S')}"

        print(f"🎮 Processing game with {game_data.totalPlayers} players...")

        # Configure processing
        workflow_config = {
            "skip_personality": config.skip_personality,
            "verbose_logging": config.verbose_logging,
        }

        # Process game data through orchestrator
        result: GameProcessingResult = await orchestrator.process_game_data(
            game_data=game_data, config=workflow_config, thread_id=thread_id
        )

        # Store debug report if requested
        if config.generate_debug_report:
            debug_reports[thread_id] = {
                "game_data": game_data.dict(),
                "result": result.dict(),
                "config": config.dict(),
                "processing_time": result.processing_time,
                "timestamp": start_time,
            }

        # Generate response data
        response_data = {
            "results": [
                player_result.dict() for player_result in result.player_results
            ],
            "game_summary": {
                "total_players": result.total_players,
                "players_with_valid_selections": len(
                    [
                        r
                        for r in result.player_results
                        if len(r.selected_ingredients) > 0
                    ]
                ),
                "players_with_all_skips": len(
                    [
                        r
                        for r in result.player_results
                        if len(r.selected_ingredients) == 0
                    ]
                ),
                "total_game_cost": result.total_cost,
                "cost_validation_summary": {
                    "frontend_values_ignored": True,
                    "backend_calculation_method": "ingredient_database",
                    "all_costs_authoritative": True,
                },
            },
            "processing_metadata": {
                "session_id": result.session_id,
                "processing_time": result.processing_time,
                "workflow_type": result.metadata.get("workflow_type", "unknown"),
                "thread_id": thread_id,
                "has_errors": len(result.processing_errors) > 0,
            },
        }

        # Add debug information if requested
        debug_info = None
        if config.verbose_logging:
            debug_info = {
                "total_reasoning_steps": sum(
                    len(r.reasoning_steps) for r in result.player_results
                ),
                "processing_errors": result.processing_errors,
                "group_summary": result.group_summary,
            }

        return APIResponse(success=True, data=response_data, debug_info=debug_info)

    except Exception as e:
        print(f"❌ Error processing game results: {str(e)}")
        return APIResponse(
            success=False,
            error=f"Processing failed: {str(e)}",
            debug_info={"error_type": type(e).__name__}
            if config.verbose_logging
            else None,
        )


@app.post("/api/process-single-player", response_model=APIResponse)
async def process_single_player(
    player_data: PlayerData, config: ProcessingConfig = ProcessingConfig()
):
    """
    Process individual player's selections (for testing or single-player scenarios).

    Useful for:
    - Testing individual player processing
    - Single-player game modes
    - Debugging specific selection patterns
    """
    try:
        print(f"👤 Processing single player: {player_data.name}")

        # Process single player
        result: ProcessingResult = await orchestrator.process_single_player(player_data)

        response_data = {
            "player_result": result.dict(),
            "cost_validation": {
                "frontend_cost_ignored": True,
                "backend_calculated_cost": result.total_cost,
                "calculation_method": "ingredient_database",
            },
        }

        return APIResponse(
            success=True,
            data=response_data,
            debug_info={
                "reasoning_steps": len(result.reasoning_steps),
                "processing_errors": len(result.processing_errors),
            }
            if config.verbose_logging
            else None,
        )

    except Exception as e:
        print(f"❌ Error processing single player: {str(e)}")
        return APIResponse(
            success=False, error=f"Single player processing failed: {str(e)}"
        )


@app.post("/api/process-game-file", response_model=APIResponse)
async def process_game_from_file(
    file: UploadFile = File(...), config: ProcessingConfig = ProcessingConfig()
):
    """
    Alternative endpoint: receives JSON file with game results.

    Useful for:
    - Batch processing from files
    - Integration testing
    - Historical game data processing
    """
    try:
        # Read and parse file
        content = await file.read()
        game_data_dict = json.loads(content)
        game_data = GameData(**game_data_dict)

        print(f"📁 Processing game from file: {file.filename}")

        # Process the game data
        return await process_game_results(game_data, config)

    except json.JSONDecodeError as e:
        return APIResponse(success=False, error=f"Invalid JSON format: {str(e)}")
    except Exception as e:
        return APIResponse(success=False, error=f"File processing failed: {str(e)}")


@app.post("/api/validate-game-costs", response_model=APIResponse)
async def validate_game_costs(request: CostValidationRequest):
    """
    Calculate authoritative costs using backend database (ignore frontend totalCost values).

    This endpoint demonstrates the cost calculation authority of the backend system.
    Frontend cost values are ignored and backend calculations are authoritative.
    """
    try:
        game_data = request.game_data

        print(f"💰 Validating costs for {len(game_data.players)} players...")

        validation_results = []
        total_frontend_cost = 0.0
        total_backend_cost = 0.0

        for player in game_data.players:
            # Calculate backend cost using MCP client
            cost_validation = await orchestrator.mcp_client.calculate_total_cost(
                player.selections
            )

            # Compare with frontend
            frontend_cost = player.totalCost
            backend_cost = cost_validation.calculated_cost
            difference = abs(frontend_cost - backend_cost)

            total_frontend_cost += frontend_cost
            total_backend_cost += backend_cost

            validation_results.append(
                {
                    "player_id": player.id,
                    "player_name": player.name,
                    "selections": player.selections,
                    "frontend_cost": frontend_cost,
                    "backend_calculated_cost": backend_cost,
                    "difference": difference,
                    "discrepancy_percentage": (difference / frontend_cost * 100)
                    if frontend_cost > 0
                    else 0,
                    "cost_validation": cost_validation.dict(),
                    "status": "BACKEND_AUTHORITATIVE",
                }
            )

        response_data = {
            "validation_results": validation_results,
            "summary": {
                "total_players": len(game_data.players),
                "total_frontend_cost": total_frontend_cost,
                "total_backend_cost": total_backend_cost,
                "total_difference": abs(total_frontend_cost - total_backend_cost),
                "backend_is_authoritative": True,
                "frontend_values_ignored_in_processing": True,
            },
        }

        return APIResponse(success=True, data=response_data)

    except Exception as e:
        return APIResponse(success=False, error=f"Cost validation failed: {str(e)}")


@app.get("/api/debug-report/{session_id}", response_model=APIResponse)
async def get_debug_report(session_id: str):
    """
    Get detailed reasoning report for a specific session.

    Provides complete debugging information including:
    - Complete reasoning traces
    - Cost calculation details
    - Personality influence analysis
    - Processing performance metrics
    """
    try:
        if session_id not in debug_reports:
            return APIResponse(
                success=False, error=f"Debug report not found for session: {session_id}"
            )

        report = debug_reports[session_id]

        # Generate enhanced debug report
        enhanced_report = {
            "session_id": session_id,
            "timestamp": report["timestamp"],
            "game_overview": {
                "total_players": report["game_data"]["totalPlayers"],
                "game_date": report["game_data"]["gameDate"],
                "processing_time": report["processing_time"],
            },
            "processing_results": report["result"],
            "configuration": report["config"],
            "debug_analysis": {
                "total_reasoning_steps": sum(
                    len(player["reasoning_steps"])
                    for player in report["result"]["player_results"]
                ),
                "cost_calculation_method": "backend_database_authoritative",
                "personality_enhancements_applied": any(
                    player.get("personality_influence")
                    for player in report["result"]["player_results"]
                ),
            },
        }

        return APIResponse(success=True, data=enhanced_report)

    except Exception as e:
        return APIResponse(
            success=False, error=f"Debug report generation failed: {str(e)}"
        )


@app.get("/api/selection-mappings", response_model=APIResponse)
async def get_selection_mappings():
    """
    Get available abstract selection mappings (Rich, Crunchy, etc.).

    Returns the current mapping configuration for game selections to ingredients.
    """
    try:
        mappings = orchestrator.mcp_client.SELECTION_MAPPINGS

        response_data = {
            "available_selections": list(mappings.keys()),
            "mappings": mappings,
            "mapping_info": {
                "total_selections": len(mappings),
                "supports_skip": "skip" in mappings,
                "premium_selections": [
                    key
                    for key, value in mappings.items()
                    if value.get("premium_factor", 1.0) > 1.0
                ],
            },
        }

        return APIResponse(success=True, data=response_data)

    except Exception as e:
        return APIResponse(
            success=False, error=f"Selection mappings retrieval failed: {str(e)}"
        )


@app.get("/api/health", response_model=APIResponse)
async def health_check():
    """Health check endpoint for monitoring."""
    try:
        # Test database connectivity
        ingredients = await orchestrator.mcp_client.get_all_ingredients()

        health_data = {
            "status": "healthy",
            "database_accessible": len(ingredients) > 0,
            "total_ingredients": len(ingredients),
            "orchestrator_ready": orchestrator is not None,
            "workflow_enabled": orchestrator.use_langgraph,
        }

        return APIResponse(success=True, data=health_data)

    except Exception as e:
        return APIResponse(success=False, error=f"Health check failed: {str(e)}")


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
