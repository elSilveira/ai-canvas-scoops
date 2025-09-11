/**
 * Enhanced AI response structure types for better data alignment
 */

export interface IngredientCostBreakdown {
  ingredient: string;
  quantity: number;
  unit_cost: number;
  total_cost: number;
  category: string;
}

export interface CostBreakdown {
  base_cost: number;
  ingredient_costs: number;
  preparation_cost: number;
  total_cost: number;
}

export interface EnhancedAIResponse {
  reasoning_steps: string[];
  ingredient_mappings: IngredientCostBreakdown[];
  similar_flavors: string[];
  probable_ice_cream: string;
  cost_breakdown: CostBreakdown;
  confidence_score: number;
}

export interface AIInteraction {
  selection: string;
  aiThought: string;
  aiEmoji: string;
  aiSteps: string[];
  round: number;
  timestamp: Date;
  enhanced_ai_response?: EnhancedAIResponse;
}

export interface IceCreamPersonality {
  name: string;
  emoji: string;
  description: string;
  insights: string[];
  color: string;
  gradient: string;
}

export interface Player {
  id: string;
  name: string;
  selections: string[];
  totalCost: number;
  aiInteractions: AIInteraction[];
  generatedImageUrl?: string;
  personality?: IceCreamPersonality;
}
