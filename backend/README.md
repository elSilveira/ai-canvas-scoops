# AI Canvas Scoops Backend

A sophisticated AI-powered ice cream customization system that processes game-based player data to generate realistic ice cream images.

## Features

- **Game Data Processing**: Converts complex game player data into structured ice cream specifications
- **Intelligent Selection Mapping**: Maps player choices to ice cream flavors, toppings, and configurations
- **Cost Calculation**: Calculates pricing based on ingredients and customizations
- **Advanced Image Generation**: Creates realistic ice cream images using Stability AI's Ultra model
- **LangGraph Workflows**: Supports complex multi-agent workflows for processing
- **FastAPI Integration**: RESTful API endpoints for frontend integration
- **MCP Server Support**: Model Context Protocol server for external integrations

## Architecture

### Core Components

- **Orchestrator**: Main agent that coordinates the entire ice cream processing workflow
- **Game Data Adapter**: Processes and validates incoming game data
- **Selection Mapping**: Maps player selections to ice cream configurations
- **Cost Calculator**: Computes pricing based on selected ingredients
- **Image Generator**: Creates high-quality ice cream images with proper stacking and presentation
- **Reasoning Tracer**: Tracks decision-making processes for transparency

### API Endpoints

- `POST /api/v1/process-game-data`: Process game data and generate ice cream
- `POST /api/v1/generate-image`: Direct image generation from specifications
- `GET /api/v1/health`: Health check endpoint

## Installation

1. Install dependencies:
```bash
uv sync
```

2. Set up environment variables:
```bash
cp .env.example .env
# Edit .env with your API keys
```

3. Run the application:
```bash
# Start FastAPI server (recommended)
python run_server.py

# Or start MCP server
uv run python src/main.py
```

## Configuration

### Environment Variables

Environment variables are loaded automatically at application startup. Copy `.env.example` to `.env` and configure:

**Required:**
- `OPENAI_API_KEY`: OpenAI API key for AI agents and language processing
  - Get from: https://platform.openai.com/account/api-keys
- `STABILITY_AI_KEY`: Stability AI API key for ice cream image generation  
  - Get from: https://platform.stability.ai/account/keys

**Optional:**
- `DB_FILE`: Path to SQLite database (defaults to `src/database/ingredients.db`)
- `DEBUG`: Enable debug mode (defaults to `false`)

### API Key Setup

1. **OpenAI API Key**: Required for all AI processing features
   - Create account at https://platform.openai.com/
   - Generate API key in account settings
   - Add to `.env` file: `OPENAI_API_KEY=your_key_here`

2. **Stability AI API Key**: Required for ice cream image generation
   - Create account at https://platform.stability.ai/
   - Generate API key in account settings  
   - Add to `.env` file: `STABILITY_AI_KEY=your_key_here`

**Note:** The application will show clear error messages if API keys are missing or invalid.

## Usage

The system processes game data through a multi-step workflow:

1. **Data Validation**: Ensures game data structure is correct
2. **Selection Processing**: Maps game choices to ice cream specifications
3. **Cost Calculation**: Computes total cost based on selections
4. **Image Generation**: Creates realistic ice cream images
5. **Result Compilation**: Returns comprehensive processing results

## Project Structure

```
src/
├── agents/           # Core processing agents
├── api/             # FastAPI application
├── database/        # Database utilities and data
├── models/          # Data models and schemas
├── tools/           # Utility tools and integrations
├── workflows/       # LangGraph workflow definitions
└── mcp/            # Model Context Protocol server
```
