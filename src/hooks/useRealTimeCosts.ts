import { useState, useEffect } from 'react';
import { getRealTimePricing, validateCost, updateInventory, type IngredientCostBreakdown } from '@/services/api';
import type { RealTimePricingResponse, CostValidationResponse, InventoryUpdateResponse } from '@/services/api';
import { toast } from 'sonner';

interface RealTimeCostState {
    totalCost: number;
    itemizedCosts: Record<string, number>;
    breakdown: {
        baseCost: number;
        ingredientCosts: Record<string, number>;
        preparationCost: number;
        markupApplied: number;
        serviceFee: number;
    };
    warnings: string[];
    aiIngredientMappings: IngredientCostBreakdown[];
    isLoading: boolean;
    error: string | null;
    lastUpdated: Date | null;
}

interface InventoryState {
    [ingredient: string]: number;
}

export const useRealTimeCosts = (playerName: string = 'Guest', sessionId?: string) => {
    const [costState, setCostState] = useState<RealTimeCostState>({
        totalCost: 0,
        itemizedCosts: {},
        breakdown: {
            baseCost: 0,
            ingredientCosts: {},
            preparationCost: 0,
            markupApplied: 0,
            serviceFee: 0
        },
        warnings: [],
        aiIngredientMappings: [],
        isLoading: false,
        error: null,
        lastUpdated: null
    });

    const [inventoryState, setInventoryState] = useState<InventoryState>({});
    const [validationHistory, setValidationHistory] = useState<CostValidationResponse[]>([]);

    /**
     * Calculate real-time pricing for selections
     */
    const calculateRealTimePricing = async (selections: string[]): Promise<RealTimePricingResponse | null> => {
        if (!selections || selections.length === 0) {
            setCostState(prev => ({
                ...prev,
                totalCost: 0,
                itemizedCosts: {},
                error: null,
                lastUpdated: new Date()
            }));
            return null;
        }

        setCostState(prev => ({ ...prev, isLoading: true, error: null }));

        try {
            console.log('💰 Calculating real-time pricing for:', selections);

            const response = await getRealTimePricing({
                selections,
                playerName,
                sessionId
            });

            if (response.success) {
                setCostState(prev => ({
                    ...prev,
                    totalCost: response.totalCost,
                    itemizedCosts: response.itemizedCosts,
                    breakdown: response.breakdown,
                    warnings: response.warnings,
                    aiIngredientMappings: response.aiIngredientMappings || [],
                    isLoading: false,
                    error: null,
                    lastUpdated: new Date()
                }));

                // Show warnings as toasts
                response.warnings.forEach(warning => {
                    toast.warning(warning);
                });

                console.log(`✅ Real-time pricing calculated: $${response.totalCost.toFixed(2)}`);
                return response;
            } else {
                throw new Error(response.error || 'Failed to calculate pricing');
            }
        } catch (error) {
            const errorMessage = error instanceof Error ? error.message : 'Failed to calculate real-time pricing';
            console.error('❌ Real-time pricing error:', errorMessage);

            setCostState(prev => ({
                ...prev,
                isLoading: false,
                error: errorMessage
            }));

            toast.error('Failed to calculate real-time pricing. Using estimated costs.');
            return null;
        }
    };

    /**
     * Validate frontend cost against backend
     */
    const validateFrontendCost = async (
        selections: string[],
        frontendCost: number
    ): Promise<CostValidationResponse | null> => {
        try {
            console.log(`🔍 Validating cost: Frontend $${frontendCost.toFixed(2)} vs Backend`);

            const response = await validateCost({
                selections,
                frontendTotalCost: frontendCost,
                playerName
            });

            if (response.success) {
                setValidationHistory(prev => [response, ...prev.slice(0, 9)]); // Keep last 10 validations

                if (!response.isValid) {
                    const discrepancyPercent = ((response.discrepancy / response.backendCost) * 100).toFixed(1);
                    toast.warning(
                        `Cost discrepancy detected: ${discrepancyPercent}% difference. Using backend calculation.`
                    );

                    // Update cost state with backend calculation
                    setCostState(prev => ({
                        ...prev,
                        totalCost: response.backendCost,
                        error: null,
                        lastUpdated: new Date()
                    }));
                } else {
                    toast.success('Cost validation passed!');
                }

                console.log(`✅ Cost validation: ${response.isValid ? 'VALID' : 'INVALID'} (${response.discrepancy.toFixed(2)} discrepancy)`);
                return response;
            } else {
                throw new Error(response.error || 'Validation failed');
            }
        } catch (error) {
            const errorMessage = error instanceof Error ? error.message : 'Failed to validate cost';
            console.error('❌ Cost validation error:', errorMessage);
            toast.error('Failed to validate cost calculation');
            return null;
        }
    };

    /**
     * Update ingredient inventory
     */
    const updateIngredientInventory = async (
        ingredient: string,
        quantity: number,
        operation: 'decrease' | 'increase' | 'set' = 'decrease'
    ): Promise<InventoryUpdateResponse | null> => {
        try {
            console.log(`📦 Updating inventory: ${ingredient} ${operation} ${quantity}`);

            const response = await updateInventory({
                ingredient,
                quantity,
                operation
            });

            if (response.success) {
                setInventoryState(prev => ({
                    ...prev,
                    [response.ingredient]: response.newQuantity
                }));

                toast.success(
                    `Inventory updated: ${response.ingredient} (${response.previousQuantity} → ${response.newQuantity})`
                );

                console.log(`✅ Inventory updated: ${response.ingredient} ${response.previousQuantity} → ${response.newQuantity}`);
                return response;
            } else {
                throw new Error(response.error || 'Failed to update inventory');
            }
        } catch (error) {
            const errorMessage = error instanceof Error ? error.message : 'Failed to update inventory';
            console.error('❌ Inventory update error:', errorMessage);
            toast.error('Failed to update ingredient inventory');
            return null;
        }
    };

    /**
     * Get cost breakdown for display
     */
    const getCostBreakdown = () => {
        return {
            ...costState.breakdown,
            total: costState.totalCost,
            formattedTotal: `$${costState.totalCost.toFixed(2)}`,
            itemizedCosts: Object.entries(costState.itemizedCosts).map(([item, cost]) => ({
                item,
                cost,
                formattedCost: `$${cost.toFixed(2)}`
            }))
        };
    };

    /**
     * Get validation status
     */
    const getValidationStatus = () => {
        const latest = validationHistory[0];
        if (!latest) return null;

        return {
            isValid: latest.isValid,
            discrepancy: latest.discrepancy,
            discrepancyPercent: ((latest.discrepancy / latest.backendCost) * 100).toFixed(1),
            tolerance: (latest.tolerance * 100).toFixed(1),
            lastValidated: new Date(latest.details.timestamp || Date.now())
        };
    };

    return {
        // State
        costState,
        inventoryState,
        validationHistory,

        // Actions
        calculateRealTimePricing,
        validateFrontendCost,
        updateIngredientInventory,

        // Computed values
        getCostBreakdown,
        getValidationStatus,

        // Helper getters
        totalCost: costState.totalCost,
        isLoading: costState.isLoading,
        error: costState.error,
        warnings: costState.warnings,
        lastUpdated: costState.lastUpdated
    };
};

export default useRealTimeCosts;
