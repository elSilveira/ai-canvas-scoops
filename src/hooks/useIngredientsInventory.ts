import { useState, useEffect } from 'react';
import { apiService, type Ingredient } from '@/services/api';
import { toast } from 'sonner';

interface GameInventoryItem {
  available: number;
  price: number;
  description: string;
  allergies: string[];
}

interface GameInventory {
  [key: string]: GameInventoryItem;
}

export const useIngredientsInventory = (playerCount: number = 4) => {
  const [inventory, setInventory] = useState<GameInventory>({});
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const loadInventory = async () => {
    try {
      setIsLoading(true);
      setError(null);

      const ingredients = await apiService.getAllIngredients();
      
      // Transform backend ingredients to game inventory format
      const gameInventory: GameInventory = {};
      
      ingredients.forEach((ingredient: Ingredient) => {
        // Map ingredient names to game values
        const gameMapping: { [key: string]: string } = {
          'Vanilla extract': 'Classic',
          'Dark chocolate (70%+ callets)': 'Rich', 
          'Lemons (fresh)': 'Light',
          'Heavy cream (35-40%)': 'Smooth',
          'Hazelnuts (roasted)': 'Crunchy',
          'Mini marshmallows': 'Sprinkles',
          'Sea-salt caramel drizzle (Jack Sparrow)': 'Caramel',
          'Rum flavoring (extract)': 'Adventure'
        };

        // Find matching game key for this ingredient
        const gameKey = gameMapping[ingredient.ingredient];
        if (gameKey) {
          // Calculate price from cost_min/cost_max or use fallback
          const basePrice = ingredient.cost_min || ingredient.cost_max || 10;
          const gamePrice = Math.round(basePrice * 20); // Scale up for game economy

          gameInventory[gameKey] = {
            available: Math.min(ingredient.inventory, playerCount * 2), // Limit based on players
            price: gamePrice,
            description: ingredient.description,
            allergies: ingredient.allergies
          };
        }
      });

      // Add fallback items if not found in database
      const fallbackInventory = {
        Adventure: { available: playerCount, price: 15, description: 'Bold and daring flavors', allergies: [] },
        Classic: { available: playerCount, price: 10, description: 'Traditional vanilla base', allergies: ['dairy'] },
        Light: { available: playerCount, price: 12, description: 'Fresh and fruity', allergies: ['citrus'] },
        Rich: { available: playerCount, price: 15, description: 'Decadent chocolate', allergies: ['milk', 'caffeine'] },
        Smooth: { available: playerCount, price: 10, description: 'Creamy texture', allergies: ['dairy'] },
        Crunchy: { available: playerCount, price: 13, description: 'Nutty crunch', allergies: ['tree_nuts'] },
        Sprinkles: { available: playerCount, price: 14, description: 'Colorful toppings', allergies: [] },
        Caramel: { available: playerCount, price: 15, description: 'Sweet caramel drizzle', allergies: ['dairy'] }
      };

      // Merge with fallbacks for missing items
      Object.keys(fallbackInventory).forEach(key => {
        if (!gameInventory[key]) {
          gameInventory[key] = fallbackInventory[key as keyof typeof fallbackInventory];
        }
      });

      setInventory(gameInventory);
      
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Failed to load ingredients';
      setError(errorMessage);
      toast.error('Failed to load ingredients from server. Using default inventory.');
      
      // Fallback to default inventory
      const defaultInventory: GameInventory = {
        Adventure: { available: playerCount, price: 15, description: 'Bold and daring flavors', allergies: [] },
        Classic: { available: playerCount, price: 10, description: 'Traditional vanilla base', allergies: ['dairy'] },
        Light: { available: playerCount, price: 12, description: 'Fresh and fruity', allergies: ['citrus'] },
        Rich: { available: playerCount, price: 15, description: 'Decadent chocolate', allergies: ['milk', 'caffeine'] },
        Smooth: { available: playerCount, price: 10, description: 'Creamy texture', allergies: ['dairy'] },
        Crunchy: { available: playerCount, price: 13, description: 'Nutty crunch', allergies: ['tree_nuts'] },
        Sprinkles: { available: playerCount, price: 14, description: 'Colorful toppings', allergies: [] },
        Caramel: { available: playerCount, price: 15, description: 'Sweet caramel drizzle', allergies: ['dairy'] }
      };
      
      setInventory(defaultInventory);
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    loadInventory();
  }, [playerCount]);

  const decreaseInventory = (itemKey: string, amount: number = 1) => {
    setInventory(prev => ({
      ...prev,
      [itemKey]: {
        ...prev[itemKey],
        available: Math.max(0, prev[itemKey].available - amount)
      }
    }));
  };

  const resetInventory = () => {
    loadInventory();
  };

  return {
    inventory,
    isLoading,
    error,
    decreaseInventory,
    resetInventory,
    refetch: loadInventory
  };
};
