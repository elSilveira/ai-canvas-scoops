import React, { useEffect, useState } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { CheckCircle, AlertTriangle, DollarSign, TrendingUp, Clock, RefreshCw } from 'lucide-react';
import { useRealTimeCosts } from '@/hooks/useRealTimeCosts';
import { apiService } from '@/services/api';

interface RealTimeCostDisplayProps {
  playerName: string;
  selections: string[];
  onCostUpdate?: (cost: number) => void;
  showValidation?: boolean;
  className?: string;
  sessionId?: string;
}

export const RealTimeCostDisplay: React.FC<RealTimeCostDisplayProps> = ({
  playerName,
  selections,
  onCostUpdate,
  showValidation = true,
  className = '',
  sessionId
}) => {
  const {
    costState,
    calculateRealTimePricing,
    getCostBreakdown,
    isLoading,
    error,
    warnings,
    lastUpdated
  } = useRealTimeCosts(playerName, sessionId);

  const [iceCreamSuggestions, setIceCreamSuggestions] = useState<{
    probableIceCream: string;
    alternativeNames: string[];
    suggestedIngredients: string[];
  } | null>(null);

  // Fetch ice cream suggestions from backend
  const fetchIceCreamSuggestions = async (playerSelections: string[]) => {
    try {
      const response = await apiService.getIceCreamSuggestions(playerSelections);
      
      if (response.success) {
        setIceCreamSuggestions({
          probableIceCream: response.probableIceCream || 'Custom Creation',
          alternativeNames: response.alternativeNames || [],
          suggestedIngredients: response.suggestedIngredients || []
        });
      }
    } catch (error) {
      console.error('Error fetching ice cream suggestions:', error);
      setIceCreamSuggestions({
        probableIceCream: 'Custom Creation',
        alternativeNames: [],
        suggestedIngredients: []
      });
    }
  };

  // Auto-update pricing when selections change
  useEffect(() => {
    if (selections && selections.length > 0) {
      calculateRealTimePricing(selections);
      fetchIceCreamSuggestions(selections);
    }
  }, [selections]);

  // Notify parent component of cost updates
  useEffect(() => {
    if (onCostUpdate && costState.totalCost > 0) {
      onCostUpdate(costState.totalCost);
    }
  }, [costState.totalCost, onCostUpdate]);

  const breakdown = getCostBreakdown();

  const handleRefreshPricing = async () => {
    if (selections.length > 0) {
      await calculateRealTimePricing(selections);
    }
  };

  if (selections.length === 0) {
    return (
      <Card className={`${className} opacity-50`}>
        <CardHeader className="pb-4">
          <CardTitle className="flex items-center gap-2 text-lg">
            <DollarSign className="w-5 h-5" />
            AI-Selected Ingredients & Costs
          </CardTitle>
        </CardHeader>
        <CardContent>
          <p className="text-muted-foreground text-center py-4">
            Make selections to see pricing
          </p>
        </CardContent>
      </Card>
    );
  }

  return (
    <Card className={className}>
      <CardHeader className="pb-4">
        <CardTitle className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <DollarSign className="w-5 h-5" />
            AI-Selected Ingredients & Costs
            {isLoading && <RefreshCw className="w-4 h-4 animate-spin" />}
          </div>
          <Button
            variant="ghost"
            size="sm"
            onClick={handleRefreshPricing}
            disabled={isLoading}
          >
            <RefreshCw className="w-4 h-4" />
          </Button>
        </CardTitle>
      </CardHeader>

      <CardContent className="space-y-4">
        {/* Error Display */}
        {error && (
          <Alert className="border-red-500/50 bg-red-500/10">
            <AlertTriangle className="w-4 h-4 text-red-500" />
            <AlertDescription className="text-red-700">
              {error}
            </AlertDescription>
          </Alert>
        )}

        {/* Warnings */}
        {warnings.length > 0 && (
          <div className="space-y-2">
            {warnings.map((warning, index) => (
              <Alert key={index} className="border-yellow-500/50 bg-yellow-500/10">
                <AlertTriangle className="w-4 h-4 text-yellow-500" />
                <AlertDescription className="text-yellow-700">
                  {warning}
                </AlertDescription>
              </Alert>
            ))}
          </div>
        )}

        {/* Total Cost */}
        <div className="flex justify-between items-center p-4 bg-gradient-to-r from-green-50 to-emerald-50 rounded-lg border">
          <div>
            <p className="text-sm font-medium text-gray-600">Total Cost</p>
            <p className="text-2xl font-bold text-green-700">
              {breakdown.formattedTotal}
            </p>
          </div>
          <div className="text-right">
            <p className="text-xs text-gray-500">
              {lastUpdated && (
                <>
                  <Clock className="w-3 h-3 inline mr-1" />
                  {lastUpdated.toLocaleTimeString()}
                </>
              )}
            </p>
            <Badge variant="secondary" className="bg-green-100 text-green-700">
              Live Pricing
            </Badge>
          </div>
        </div>

        {/* AI-Selected Ingredients */}
        {costState.aiIngredientMappings.length > 0 ? (
          <div>
            {/* <h4 className="font-medium text-sm text-gray-700 mb-2">AI-Selected Ingredients</h4>
            <div className="space-y-2">
              {costState.aiIngredientMappings.map((ingredient, idx) => (
                <div key={idx} className="flex justify-between items-center bg-blue-50/50 rounded-lg px-3 py-2">
                  <div className="flex items-center gap-2">
                    <span className={`w-2 h-2 rounded-full ${
                      ingredient.category === 'flavor' ? 'bg-purple-400' :
                      ingredient.category === 'texture' ? 'bg-blue-400' :
                      'bg-orange-400'
                    }`}></span>
                    <span className="text-sm font-medium">{ingredient.ingredient}</span>
                    <span className="text-xs text-muted-foreground">({ingredient.quantity}x)</span>
                  </div>
                  <span className="text-sm font-semibold text-green-600">${ingredient.total_cost.toFixed(2)}</span>
                </div>
              ))}
            </div> */}
          </div>
        ) : breakdown.itemizedCosts.length > 0 && (
          <div>
            {/* <h4 className="font-medium text-sm text-gray-700 mb-2">Player Selections</h4>
            <div className="space-y-1">
              {breakdown.itemizedCosts.map(({ item, formattedCost }) => (
                <div key={item} className="flex justify-between text-sm">
                  <span className="text-gray-600">{item}</span>
                  <span className="font-medium">{formattedCost}</span>
                </div>
              ))}
            </div> */}
          </div>
        )}

        {/* Cost Breakdown */}
        {breakdown.baseCost > 0 && (
          <div>
            <h4 className="font-medium text-sm text-gray-700 mb-2">Cost Breakdown</h4>
            <div className="space-y-1 text-sm">
              <div className="flex justify-between">
                <span className="text-gray-600">Base Ingredients</span>
                <span>${breakdown.baseCost.toFixed(2)}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-600">Preparation</span>
                <span>${breakdown.preparationCost.toFixed(2)}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-600">Service Fee</span>
                <span>${breakdown.serviceFee.toFixed(2)}</span>
              </div>
              {breakdown.markupApplied > 0 && (
                <div className="flex justify-between">
                  <span className="text-gray-600">Premium Markup</span>
                  <span>${breakdown.markupApplied.toFixed(2)}</span>
                </div>
              )}
            </div>
          </div>
        )}

        {/* Ice Cream Information - Show probable ice cream name and ingredients */}
        {showValidation && (
          <div className="pt-4 border-t">
            <h4 className="font-medium text-sm text-gray-700 mb-2">Ice Cream Profile</h4>
            
            <div className="space-y-2">
              <div className="text-sm">
                <span className="text-gray-600">Probable Ice Cream:</span>
                <span className="font-medium ml-2">
                  {iceCreamSuggestions?.probableIceCream || 'Custom Creation'}
                </span>
              </div>
              
              {iceCreamSuggestions?.alternativeNames && iceCreamSuggestions.alternativeNames.length > 0 && (
                <div className="text-sm">
                  <span className="text-gray-600">Similar Flavors:</span>
                  <div className="mt-1 flex flex-wrap gap-1">
                    {iceCreamSuggestions.alternativeNames.slice(0, 3).map((name, index) => (
                      <Badge key={index} variant="outline" className="text-xs">
                        {name}
                      </Badge>
                    ))}
                  </div>
                </div>
              )}
              
              <div className="text-sm">
                <span className="text-gray-600">Key Ingredients:</span>
                <div className="mt-1 flex flex-wrap gap-1">
                  {iceCreamSuggestions?.suggestedIngredients?.length > 0 ? (
                    iceCreamSuggestions.suggestedIngredients.slice(0, 5).map((ingredient, index) => (
                      <Badge key={index} variant="secondary" className="text-xs">
                        {ingredient}
                      </Badge>
                    ))
                  ) : (
                    selections.map((selection, index) => (
                      <Badge key={index} variant="outline" className="text-xs">
                        {selection}
                      </Badge>
                    ))
                  )}
                </div>
              </div>
            </div>
          </div>
        )}

        {/* Player Info */}
        <div className="text-xs text-gray-500 text-center pt-2 border-t">
          Pricing for: {playerName} • {selections.length} selection{selections.length !== 1 ? 's' : ''}
        </div>
      </CardContent>
    </Card>
  );
};
