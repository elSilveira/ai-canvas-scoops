// API service for communicating with the backend
const BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api/v1';

// Health check endpoint
export const checkHealth = async (): Promise<{ status: string; message: string }> => {
  const response = await fetch(`${BASE_URL}/health`);
  if (!response.ok) {
    throw new Error('Health check failed');
  }
  return response.json();
};

// Get selection mappings
export const getSelectionMappingsLegacy = async (): Promise<SelectionMapping[]> => {
  const response = await fetch(`${BASE_URL}/selection-mappings`);
  if (!response.ok) {
    throw new Error('Failed to fetch selection mappings');
  }
  return response.json();
};

export interface Ingredient {
  ingredient: string;
  description: string;
  used_on: string[];
  allergies: string[];
  quantity: string;
  cost_min: number | null;
  cost_max: number | null;
  inventory: number;
}

export interface FinalRevealData {
  player_name: string;
  character: string;
  ice_cream_data: {
    personality: {
      name: string;
      emoji: string;
      description: string;
      insights: string[];
      color: string;
      gradient: string;
    };
    selections: string[];
    aiInteractions: Array<{
      selection: string;
      aiThought: string;
      aiEmoji: string;
      aiSteps: string[];
      round: number;
      timestamp: Date;
    }>;
  };
  ingredients_used: string[];
  total_cost: number | null;
}

export interface GameResultData {
  gameDate: string;
  players: Array<{
    id: string;
    name: string;
    selections: string[];
    totalCost: number;
    aiInteractions: Array<{
      selection: string;
      aiThought: string;
      aiEmoji: string;
      aiSteps: string[];
      round: number;
      timestamp: Date;
    }>;
    personality: {
      name: string;
      emoji: string;
      description: string;
      insights: string[];
      color: string;
      gradient: string;
    };
  }>;
  totalPlayers: number;
  gameVersion: string;
}

// New interfaces for Phase 1 integration
export interface PlayerGameData {
  id: string;
  name: string;
  selections: string[];
  personality?: {
    name: string;
    emoji: string;
    description: string;
    insights: string[];
    color: string;
    gradient: string;
  };
}

export interface ProcessingConfig {
  generateImage?: boolean;
  verbose?: boolean;
  qualityLevel?: 'fast' | 'balanced' | 'high';
  session_id?: string;
}

export interface IngredientCostBreakdown {
  ingredient: string;
  quantity: number;
  unit_cost: number;
  total_cost: number;
  category: string;
}

export interface EnhancedAIResponse {
  reasoning_steps: string[];
  ingredient_mappings: IngredientCostBreakdown[];
  similar_flavors: string[];
  probable_ice_cream: string;
  cost_breakdown: {
    base_cost: number;
    ingredient_costs: number;
    preparation_cost: number;
    total_cost: number;
  };
  confidence_score: number;
}

export interface ProcessedGameResult {
  success: boolean;
  data: {
    processedResults: {
      player_name: string;
      total_cost: number;
      selected_ingredients: string[];
      reasoning_steps: string[];
      processing_errors: string[];
      enhanced_ai_response?: EnhancedAIResponse;
    };
    imageUrl?: string;
    estimatedCost: number;
    ingredientsUsed: string[];
    aiReasoningSteps: string[];
  };
  error?: string;
}

export interface ImageGenerationResult {
  success: boolean;
  imageUrl?: string;
  metadata?: {
    prompt: string;
    processingTime: string;
    model: string;
    ingredients: string[];
    style: string;
    size: string;
  };
  error?: string;
}

export interface SelectionMapping {
  frontendChoice: string;
  backendIngredient: string;
  category: string;
  description: string;
}

// Phase 3.3 - Cost Calculation Integration Interfaces
export interface RealTimePricingRequest {
  selections: string[];
  playerName?: string;
  sessionId?: string;
}

export interface RealTimePricingResponse {
  success: boolean;
  totalCost: number;
  itemizedCosts: Record<string, number>;
  currency: string;
  breakdown: {
    baseCost: number;
    ingredientCosts: Record<string, number>;
    preparationCost: number;
    markupApplied: number;
    serviceFee: number;
  };
  warnings: string[];
  aiIngredientMappings?: IngredientCostBreakdown[];
  error?: string;
}

export interface InventoryUpdateRequest {
  ingredient: string;
  quantity: number;
  operation: 'decrease' | 'increase' | 'set';
}

export interface InventoryUpdateResponse {
  success: boolean;
  ingredient: string;
  previousQuantity: number;
  newQuantity: number;
  error?: string;
}

export interface CostValidationRequest {
  selections: string[];
  frontendTotalCost: number;
  playerName?: string;
}

export interface CostValidationResponse {
  success: boolean;
  isValid: boolean;
  frontendCost: number;
  backendCost: number;
  discrepancy: number;
  tolerance: number;
  details: Record<string, any>;
  error?: string;
}

class ApiService {
  private async request<T>(endpoint: string, options?: RequestInit): Promise<T> {
    const url = `${BASE_URL}${endpoint}`;

    try {
      const response = await fetch(url, {
        headers: {
          'Content-Type': 'application/json',
          ...options?.headers,
        },
        ...options,
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      return await response.json();
    } catch (error) {
      console.error(`API request failed for ${endpoint}:`, error);
      throw error;
    }
  }

  async getAllIngredients(): Promise<Ingredient[]> {
    return this.request<Ingredient[]>('/ingredients');
  }

  async saveFinalReveal(data: FinalRevealData): Promise<any> {
    return this.request('/final-reveal', {
      method: 'POST',
      body: JSON.stringify(data),
    });
  }

  async saveGameResults(data: GameResultData): Promise<any> {
    return this.request('/game-results', {
      method: 'POST',
      body: JSON.stringify(data),
    });
  }

  async healthCheck(): Promise<{ status: string; service: string }> {
    return this.request('/health');
  }

  // New Phase 1 API methods
  async processPlayerGame(
    playerData: PlayerGameData,
    processingConfig: ProcessingConfig = {}
  ): Promise<ProcessedGameResult> {
    return this.request('/process-player-game', {
      method: 'POST',
      body: JSON.stringify({
        playerData,
        processingConfig: {
          generateImage: true,
          verbose: false,
          qualityLevel: 'balanced',
          ...processingConfig
        }
      }),
    });
  }

  async generateIceCreamImage(
    selections: string[],
    playerName: string,
    style: string = 'realistic',
    size: string = '1024x1024'
  ): Promise<ImageGenerationResult> {
    return this.request('/generate-ice-cream-image', {
      method: 'POST',
      body: JSON.stringify({
        selections,
        playerName,
        style,
        size
      }),
    });
  }

  async getSelectionMappings(): Promise<SelectionMapping[]> {
    return this.request<SelectionMapping[]>('/selection-mappings');
  }

  // ===== PHASE 3.3 - COST CALCULATION INTEGRATION METHODS =====

  /**
   * Get real-time pricing for player selections
   */
  async getRealTimePricing(request: RealTimePricingRequest): Promise<RealTimePricingResponse> {
    return this.request<RealTimePricingResponse>('/real-time-pricing', {
      method: 'POST',
      body: JSON.stringify(request),
    });
  }

  /**
   * Update ingredient inventory in real-time
   */
  async updateInventory(request: InventoryUpdateRequest): Promise<InventoryUpdateResponse> {
    return this.request<InventoryUpdateResponse>('/update-inventory', {
      method: 'POST',
      body: JSON.stringify(request),
    });
  }

  /**
   * Validate frontend cost calculations against backend
   */
  async validateCost(request: CostValidationRequest): Promise<CostValidationResponse> {
    return this.request<CostValidationResponse>('/validate-cost', {
      method: 'POST',
      body: JSON.stringify(request),
    });
  }

  /**
   * Get ice cream suggestions based on player selections
   */
  async getIceCreamSuggestions(selections: string[]): Promise<{
    success: boolean;
    probableIceCream?: string;
    alternativeNames?: string[];
    suggestedIngredients?: string[];
    error?: string;
  }> {
    return this.request('/get-ice-cream-suggestions', {
      method: 'POST',
      body: JSON.stringify({ selections }),
    });
  }

  // ===== SESSION MANAGEMENT METHODS =====

  /**
   * Create a new game session
   */
  async createSession(players: any[], gameMetadata: any = {}): Promise<{
    success: boolean;
    session_id?: string;
    message?: string;
    error?: string;
  }> {
    return this.request('/session/create', {
      method: 'POST',
      body: JSON.stringify({
        players,
        game_metadata: gameMetadata
      }),
    });
  }

  /**
   * Get session status
   */
  async getSessionStatus(sessionId: string): Promise<{
    session_id: string;
    status: string;
    created_at: string;
    updated_at: string;
    players_count: number;
    expires_at: string;
  }> {
    return this.request(`/session/${sessionId}/status`);
  }

  /**
   * Get session results
   */
  async getSessionResults(sessionId: string): Promise<{
    success: boolean;
    data?: any;
    error?: string;
  }> {
    return this.request(`/session/${sessionId}/results`);
  }

  /**
   * Complete a session
   */
  async completeSession(sessionId: string): Promise<{
    success: boolean;
    message?: string;
    error?: string;
  }> {
    return this.request(`/session/${sessionId}/complete`, {
      method: 'POST',
    });
  }

  /**
   * Generate ice cream image on demand
   */
  async generateIceCreamImageOnDemand(
    playerName: string,
    sessionId?: string
  ): Promise<{
    success: boolean;
    imageUrl?: string;
    metadata?: any;
    error?: string;
  }> {
    const params = new URLSearchParams({ player: playerName });
    if (sessionId) {
      params.append('session_id', sessionId);
    }
    
    return this.request(`/generate-ice-cream-image?${params.toString()}`);
  }
}

export const apiService = new ApiService();

// Phase 7 - Image Generation API Functions
export const triggerImageGeneration = async (playerName: string, sessionId?: string): Promise<{
  success: boolean;
  imageUrl?: string;
  taskId?: string;
  error?: string;
}> => {
  const params = new URLSearchParams({ player: playerName });
  if (sessionId) {
    params.append('session_id', sessionId);
  }
  
  const response = await fetch(`${BASE_URL}/generate-ice-cream-image?${params.toString()}`);
  if (!response.ok) {
    throw new Error('Failed to trigger image generation');
  }
  return response.json();
};

export const checkImageGenerationStatus = async (taskId: string): Promise<{
  status: 'pending' | 'completed' | 'failed';
  imageUrl?: string;
  error?: string;
}> => {
  const response = await fetch(`${BASE_URL}/image-generation-status/${taskId}`);
  if (!response.ok) {
    throw new Error('Failed to check image generation status');
  }
  return response.json();
};

// Export individual methods for convenience
export const processPlayerGame = (data: any) => apiService.processPlayerGame(data);
export const generateIceCreamImage = (selections: string[], playerName: string, style = 'realistic', size = '1024x1024') =>
  apiService.generateIceCreamImage(selections, playerName, style, size);
export const getSelectionMappings = () => apiService.getSelectionMappings();

// Phase 3.3 - Cost Calculation Integration exports
export const getRealTimePricing = (request: RealTimePricingRequest) => apiService.getRealTimePricing(request);
export const updateInventory = (request: InventoryUpdateRequest) => apiService.updateInventory(request);
export const validateCost = (request: CostValidationRequest) => apiService.validateCost(request);
