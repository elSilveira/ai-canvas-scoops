// API service for communicating with the backend
const API_BASE_URL = 'http://localhost:8000/api/v1';

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

class ApiService {
  private async request<T>(endpoint: string, options?: RequestInit): Promise<T> {
    const url = `${API_BASE_URL}${endpoint}`;
    
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
}

export const apiService = new ApiService();
