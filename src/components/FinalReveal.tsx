import { Button } from "@/components/ui/button";
import { Share2, RotateCcw, Sparkles, Download, MessageSquare, ImageIcon, Loader2 } from "lucide-react";
import { useState, useEffect } from "react";
import { apiService, triggerImageGeneration, type GameResultData } from "@/services/api";
import { RealTimeCostDisplay } from "./RealTimeCostDisplay";

export interface IceCreamPersonality {
  name: string;
  emoji: string;
  description: string;
  insights: string[];
  color: string;
  gradient: string;
}

interface AIInteraction {
  selection: string;
  aiThought: string;
  aiEmoji: string;
  aiSteps: string[];
  round: number;
  timestamp: Date;
  enhanced_ai_response?: {
    reasoning_steps: string[];
    ingredient_mappings: Array<{
      ingredient: string;
      quantity: number;
      unit_cost: number;
      total_cost: number;
      category: string;
    }>;
    similar_flavors: string[];
    probable_ice_cream: string;
    cost_breakdown: {
      base_cost: number;
      ingredient_costs: number;
      preparation_cost: number;
      total_cost: number;
    };
    confidence_score: number;
  };
}

interface Player {
  id: string;
  name: string;
  selections: string[];
  totalCost: number;
  aiInteractions: AIInteraction[];
  generatedImageUrl?: string;
}

interface FinalRevealProps {
  players: Player[];
  generatePersonality: (selections: string[]) => IceCreamPersonality;
  onPlayAgain: () => void;
  onShare: () => void;
  gameSessionId: string;
}

export const FinalReveal = ({ 
  players,
  generatePersonality,
  onPlayAgain, 
  onShare,
  gameSessionId
}: FinalRevealProps) => {
  const [isRevealed, setIsRevealed] = useState(false);
  const [showInteractions, setShowInteractions] = useState<string | null>(null);
  const [isSavingData, setIsSavingData] = useState(false);
  const [gameData, setGameData] = useState<any>(null);

  // Phase 7: Image Generation Component
  const ImageGenerationDisplay = ({ player, personality }: { player: Player, personality: IceCreamPersonality }) => {
    const [imageUrl, setImageUrl] = useState<string | null>(player.generatedImageUrl || null);
    const [isLoading, setIsLoading] = useState(false);
    const [error, setError] = useState<string | null>(null);
    const [retryCount, setRetryCount] = useState(0);
    const maxRetries = 3;
    const retryDelay = 10000; // 10 seconds between retries
    const maxWaitTime = 120000; // 2 minutes maximum wait time
    
    // Use the shared game session ID for proper request differentiation
    // This ensures all players in the same game share the same session_id,
    // while the player parameter differentiates individual requests
    const sessionId = gameSessionId;
    
    // Auto-fetch generated image when component mounts
    useEffect(() => {
      const fetchGeneratedImage = async () => {
        if (imageUrl) return; // Already have an image
        
        setIsLoading(true);
        setError(null);
        
        const startTime = Date.now();
        
        const attemptFetch = async (attemptNumber: number): Promise<void> => {
          try {
            console.log(`🖼️ Attempt ${attemptNumber}: Fetching generated image for ${player.name} (session: ${sessionId})...`);
            const response = await triggerImageGeneration(player.name, sessionId);
            
            if (response.success && response.imageUrl) {
              setImageUrl(response.imageUrl);
              console.log(`✅ Successfully fetched generated image for ${player.name}`);
              setIsLoading(false);
              return;
            } 
            
            // Check if we should retry
            const elapsedTime = Date.now() - startTime;
            if (attemptNumber < maxRetries && elapsedTime < maxWaitTime) {
              console.log(`⏳ Image not ready for ${player.name}, retrying in ${retryDelay/1000}s... (${attemptNumber}/${maxRetries})`);
              setRetryCount(attemptNumber);
              
              await new Promise(resolve => setTimeout(resolve, retryDelay));
              return attemptFetch(attemptNumber + 1);
            } else {
              // Max retries reached or timeout
              if (elapsedTime >= maxWaitTime) {
                console.warn(`⏰ Timeout reached for ${player.name} after ${maxWaitTime/1000}s`);
                setError('Image generation is taking longer than expected. Please refresh to try again.');
              } else {
                console.warn(`⚠️ No generated image available for ${player.name} after ${maxRetries} attempts`);
                setError('Image generation failed after multiple attempts');
              }
              setIsLoading(false);
            }
          } catch (err) {
            console.error(`❌ Error fetching generated image for ${player.name}:`, err);
            
            const elapsedTime = Date.now() - startTime;
            if (attemptNumber < maxRetries && elapsedTime < maxWaitTime) {
              console.log(`🔄 Retrying due to error in ${retryDelay/1000}s... (${attemptNumber}/${maxRetries})`);
              setRetryCount(attemptNumber);
              
              await new Promise(resolve => setTimeout(resolve, retryDelay));
              return attemptFetch(attemptNumber + 1);
            } else {
              setError('Failed to load generated image');
              setIsLoading(false);
            }
          }
        };
        
        await attemptFetch(1);
      };
      
      fetchGeneratedImage();
    }, [player.name, imageUrl, sessionId]);
    
    const currentImageUrl = imageUrl;
    
    return (
      <div className="space-y-2">
        <div 
          className="mx-auto w-32 h-32 rounded-full overflow-hidden shadow-glow animate-bounce border-4 relative"
          style={{ 
            background: currentImageUrl ? 'transparent' : personality.gradient,
            borderColor: personality.color,
            boxShadow: `0 0 30px ${personality.color}40`
          }}
        >
          {/* Generated Image */}
          {currentImageUrl ? (
            <img 
              src={currentImageUrl} 
              alt={`${player.name}'s AI-generated ice cream`}
              className="w-full h-full object-cover rounded-full"
              onLoad={() => {
                console.log(`✅ Successfully loaded generated image for ${player.name}`);
              }}
              onError={(e) => {
                console.warn(`Failed to load generated image for ${player.name}, falling back to emoji`);
                e.currentTarget.style.display = 'none';
                const fallbackDiv = e.currentTarget.nextElementSibling as HTMLElement;
                if (fallbackDiv) fallbackDiv.style.display = 'flex';
              }}
            />
          ) : null}
          
          {/* Emoji Fallback */}
          <div 
            className="w-full h-full flex items-center justify-center text-5xl"
            style={{ display: currentImageUrl ? 'none' : 'flex' }}
          >
            {personality.emoji}
          </div>
          
          {/* Loading Overlay */}
          {isLoading && (
            <div className="absolute inset-0 bg-black/50 flex flex-col items-center justify-center rounded-full text-white text-xs">
              <Loader2 className="w-6 h-6 animate-spin mb-1" />
              <div className="text-center">
                <div>Generating...</div>
                {retryCount > 0 && (
                  <div className="text-xs opacity-80">
                    Attempt {retryCount + 1}/{maxRetries}
                  </div>
                )}
              </div>
            </div>
          )}
        </div>
        
        {/* Loading Status */}
        {isLoading && (
          <p className="text-xs text-muted-foreground text-center">
            Loading AI-generated image...
          </p>
        )}
        
        {error && (
          <p className="text-xs text-red-500 text-center">
            {error}
          </p>
        )}
      </div>
    );
  };

  useEffect(() => {
    // Generate the game data once when the component mounts
    const generatedGameData = {
      gameDate: new Date().toISOString(),
      players: players.map(player => ({
        ...player,
        personality: generatePersonality(player.selections),
        aiInteractions: player.aiInteractions
      })),
      totalPlayers: players.length,
      gameVersion: "1.0"
    };
    setGameData(generatedGameData);

    const timer = setTimeout(() => {
      setIsRevealed(true);
      // Save data to backend after reveal
      saveGameDataToBackend(generatedGameData);
    }, 500);
    return () => clearTimeout(timer);
  }, []);

  const saveGameDataToBackend = async (dataToSave?: any) => {
    const gameDataToSave = dataToSave || gameData;
    if (!gameDataToSave) return;

    setIsSavingData(true);
    try {
      // Send the data to the backend
      const response = await apiService.saveGameResults(gameDataToSave);
      console.log('Game data successfully saved to backend!', response);
    } catch (error) {
      console.error('Failed to save game data:', error);
      // You could show a toast notification here
    } finally {
      setIsSavingData(false);
    }
  };

  const downloadGameData = () => {
    if (!gameData) return;

    const dataStr = JSON.stringify(gameData, null, 2);
    const dataBlob = new Blob([dataStr], { type: 'application/json' });
    const url = URL.createObjectURL(dataBlob);
    
    const link = document.createElement('a');
    link.href = url;
    link.download = `ice-cream-game-${new Date().toISOString().split('T')[0]}.json`;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    URL.revokeObjectURL(url);
  };

  return (
    <div className="min-h-screen bg-gradient-canvas p-6 flex items-center justify-center">
      <div className="max-w-6xl mx-auto w-full space-y-8">
        {/* Celebration Header */}
        <div className="text-center space-y-4 animate-fade-in">
          <div className="flex items-center justify-center gap-2 text-ai-primary">
            <Sparkles className="w-6 h-6" />
            <span className="text-lg font-semibold">Final Results</span>
            <Sparkles className="w-6 h-6" />
          </div>
          <h1 className="text-4xl md:text-5xl font-bold text-foreground">
            Ice Cream Personalities Revealed!
          </h1>
        </div>

        {/* Players Grid */}
        <div className={`grid gap-6 ${players.length === 1 ? 'grid-cols-1' : players.length === 2 ? 'grid-cols-1 md:grid-cols-2' : 'grid-cols-1 md:grid-cols-2 lg:grid-cols-3'} transition-all duration-1000 ${isRevealed ? 'animate-scale-in' : 'scale-50 opacity-0'}`}>
        {players.map((player, index) => {
          const personality = generatePersonality(player.selections);
          const isEmptyPlayer = player.selections.every(s => s === 'Skip');
          
          return (
              <div 
                key={player.id}
                className={`backdrop-blur-sm rounded-3xl p-6 border shadow-ai-glow transition-all duration-500 hover:scale-[1.02] ${
                  isEmptyPlayer 
                    ? 'bg-gradient-to-br from-slate-200/50 to-slate-300/50 dark:from-slate-700/50 dark:to-slate-800/50 border-dashed border-slate-400' 
                    : 'bg-surface-elevated/50 border-border/30'
                }`}
                style={!isEmptyPlayer ? { animationDelay: `${index * 0.2}s` } : { 
                  animationDelay: `${index * 0.2}s`,
                  boxShadow: '0 0 30px rgba(148, 163, 184, 0.3)'
                }}
              >
                {/* Easter Egg Alert for Empty Players */}
                {isEmptyPlayer && (
                  <div className="text-center mb-4 p-3 bg-slate-100 dark:bg-slate-800 rounded-xl border border-dashed border-slate-400">
                    <div className="text-2xl mb-2">🎉 EASTER EGG FOUND! 🎉</div>
                    <div className="text-xs font-bold text-slate-600 dark:text-slate-400 uppercase tracking-wider">
                      Skip Master Achievement Unlocked!
                    </div>
                  </div>
                )}
                
                {/* Player Name & Cost */}
                <div className="space-y-4">
                  <div className="flex items-center justify-between">
                    <h3 className={`text-xl font-bold ${
                      isEmptyPlayer ? 'text-slate-700 dark:text-slate-300' : 'text-foreground'
                    }`}>{player.name}</h3>
                    <span className={`text-lg font-semibold ${
                      isEmptyPlayer ? 'text-slate-500 dark:text-slate-400' : 'text-emerald-400'
                    }`}>
                      Total Cost: ${player.totalCost}
                    </span>
                  </div>

                  {/* Phase 3.3 - Real-time Cost Validation */}
                  {!isEmptyPlayer && player.selections.length > 0 && (
                    <div className="mt-4">
                      {/* <RealTimeCostDisplay
                        playerName={player.name}
                        selections={player.selections}
                        showValidation={true}
                        className="bg-white/5 backdrop-blur-sm border-white/10"
                      /> */}
                    </div>
                  )}

                  {/* Ice Cream Visual */}
                  <div className="text-center space-y-4 mb-6">
                    {isEmptyPlayer ? (
                      <div className="mx-auto w-32 h-32 rounded-2xl overflow-hidden shadow-glow animate-pulse border-2 border-dashed border-slate-400">
                        <img 
                          src="https://media1.tenor.com/m/_BiwWBWhYucAAAAd/what-huh.gif" 
                          alt="Confused reaction GIF"
                          className="w-full h-full object-cover"
                        />
                      </div>
                    ) : (
                      <ImageGenerationDisplay player={player} personality={personality} />
                    )}
                    <div className="space-y-2">
                      <h4 className={`text-lg font-bold ${
                        isEmptyPlayer 
                          ? 'text-slate-700 dark:text-slate-300' 
                          : 'bg-gradient-ai bg-clip-text text-transparent'
                      }`}>
                        {personality.name}
                      </h4>
                      <p className={`text-sm ${
                        isEmptyPlayer ? 'text-slate-600 dark:text-slate-400' : 'text-muted-foreground'
                      }`}>
                        {personality.description}
                      </p>
                    </div>
                  </div>

                  {/* AI-Determined Ingredients & Costs */}
                  {!isEmptyPlayer && player.aiInteractions && player.aiInteractions.length > 0 && (
                    <div className="mb-4">
                      <h5 className="text-sm font-semibold mb-2 text-center text-foreground">
                        AI-Selected Ingredients & Costs
                      </h5>
                      {/* Try to get enhanced AI response from the latest interaction */}
                      {(() => {
                        // Get the enhanced AI response from the backend if available
                        const latestInteraction = player.aiInteractions[player.aiInteractions.length - 1];
                        const enhancedResponse = latestInteraction?.enhanced_ai_response;
                        
                        if (enhancedResponse && enhancedResponse.ingredient_mappings) {
                          return (
                            <div className="space-y-2">
                              {enhancedResponse.ingredient_mappings.map((ingredient, idx) => (
                                <div key={idx} className="flex justify-between items-center bg-surface/30 rounded-lg px-3 py-2">
                                  <div className="flex items-center gap-2">
                                    <span className={`w-2 h-2 rounded-full ${
                                      ingredient.category === 'flavor' ? 'bg-purple-400' :
                                      ingredient.category === 'texture' ? 'bg-blue-400' :
                                      'bg-orange-400'
                                    }`}></span>
                                    <span className="text-sm font-medium">{ingredient.ingredient}</span>
                                    <span className="text-xs text-muted-foreground">({ingredient.quantity}x)</span>
                                  </div>
                                  <span className="text-sm font-semibold text-emerald-400">${ingredient.total_cost}</span>
                                </div>
                              ))}
                              <div className="pt-2 mt-2 border-t border-border/20">
                                <div className="flex justify-between items-center">
                                  <span className="text-sm font-semibold">Total Ingredients:</span>
                                  <span className="text-lg font-bold text-emerald-400">
                                    ${enhancedResponse.cost_breakdown?.total_cost || player.totalCost}
                                  </span>
                                </div>
                              </div>
                            </div>
                          );
                        }
                        
                        // Fallback: show basic ingredient mapping if no enhanced response
                        return (
                          <div className="text-center text-muted-foreground text-sm">
                            Ingredient breakdown not available
                          </div>
                        );
                      })()}
                    </div>
                  )}

                  {/* Similar Flavors Recommendations */}
                  {!isEmptyPlayer && player.aiInteractions && player.aiInteractions.length > 0 && (
                    <div className="mb-4">
                      <h5 className="text-sm font-semibold mb-2 text-center text-foreground">
                        You Might Also Like
                      </h5>
                      {(() => {
                        const latestInteraction = player.aiInteractions[player.aiInteractions.length - 1];
                        const enhancedResponse = latestInteraction?.enhanced_ai_response;
                        
                        if (enhancedResponse && enhancedResponse.similar_flavors && enhancedResponse.similar_flavors.length > 0) {
                          // Filter out any flavors that match the probable ice cream
                          const uniqueSimilarFlavors = enhancedResponse.similar_flavors.filter(flavor => 
                            flavor !== enhancedResponse.probable_ice_cream
                          );

                          return (
                            <div className="space-y-2">
                              <div className="bg-gradient-ai/10 rounded-lg p-3 border border-ai-primary/20">
                                <div className="flex items-center gap-2 mb-2">
                                  <span className="text-lg">🍦</span>
                                  <span className="text-sm font-semibold text-ai-primary">Most Probable Match:</span>
                                </div>
                                <span className="text-sm font-medium">{enhancedResponse.probable_ice_cream}</span>
                              </div>
                              
                              {uniqueSimilarFlavors.length > 0 && (
                                <div className="space-y-1">
                                  <div className="text-xs text-muted-foreground text-center">Alternative Recommendations:</div>
                                  <div className="flex flex-wrap justify-center gap-1">
                                    {uniqueSimilarFlavors.map((flavor, idx) => (
                                      <div key={idx} className="px-2 py-1 rounded-full text-xs bg-surface/50 text-foreground border border-border/30">
                                        {flavor}
                                      </div>
                                    ))}
                                  </div>
                                </div>
                              )}
                            </div>
                          );
                        }
                        
                        return (
                          <div className="text-center text-muted-foreground text-sm">
                            Similar flavor recommendations not available
                          </div>
                        );
                      })()}
                    </div>
                  )}

                  {/* Player's Original Selections (for reference) */}
                  <div className="mb-4">
                    <h5 className={`text-sm font-semibold mb-2 text-center ${
                      isEmptyPlayer ? 'text-slate-600 dark:text-slate-400' : 'text-foreground'
                    }`}>
                      {isEmptyPlayer ? 'Skip Journey' : 'Original Flavor Choices'}
                    </h5>
                    <div className="flex flex-wrap justify-center gap-2">
                      {player.selections.map((selection, selIndex) => (
                        <div 
                          key={selIndex}
                          className={`px-2 py-1 rounded-full text-xs border ${
                            isEmptyPlayer 
                              ? 'bg-slate-200 dark:bg-slate-700 text-slate-600 dark:text-slate-300 border-slate-300 dark:border-slate-600' 
                              : 'bg-gradient-ai/10 text-foreground border-ai-primary/20'
                          } ${selection === 'Skip' ? 'animate-pulse' : ''}`}
                        >
                          {selection === 'Skip' ? '🙈 Skip' : selection}
                        </div>
                      ))}
                    </div>
                  </div>

                  {/* Key Insight */}
                  <div className="text-center">
                    <div className="flex items-start justify-center gap-2">
                      <div className={`p-1 rounded-full mt-0.5 ${
                        isEmptyPlayer ? 'bg-slate-300 dark:bg-slate-600' : 'bg-ai-primary/20'
                      }`}>
                        <Sparkles className={`w-3 h-3 ${
                          isEmptyPlayer ? 'text-slate-500 dark:text-slate-400' : 'text-ai-primary'
                        }`} />
                      </div>
                      <p className={`text-sm text-center ${
                        isEmptyPlayer ? 'text-slate-600 dark:text-slate-400' : 'text-foreground'
                      }`}>
                        {personality.insights[0]}
                      </p>
                    </div>
                  </div>

                  {/* AI Interactions Button */}
                  <div className="text-center mt-4">
                    <Button
                      onClick={() => setShowInteractions(showInteractions === player.id ? null : player.id)}
                      variant="outline"
                      size="sm"
                      className={isEmptyPlayer 
                        ? "border-slate-400 text-slate-600 dark:text-slate-400 hover:bg-slate-200 dark:hover:bg-slate-700"
                        : "border-ai-primary/30 text-ai-primary hover:bg-ai-primary/10"
                      }
                    >
                      <MessageSquare className="w-4 h-4 mr-2" />
                      {showInteractions === player.id ? 'Hide' : 'View'} {isEmptyPlayer ? 'Skip' : 'AI'} Journey
                    </Button>
                  </div>

                  {/* AI Interactions */}
                  {showInteractions === player.id && (
                    <div className="mt-4 space-y-4 bg-surface/20 rounded-lg p-4 border border-border/20 max-h-96 overflow-y-auto">
                      <div className="flex items-center justify-center gap-2 mb-3">
                        <div className="w-8 h-8 rounded-full bg-gradient-ai flex items-center justify-center">
                          <span className="text-white text-sm">🤖</span>
                        </div>
                        <h6 className="text-sm font-semibold text-ai-primary">AI Agent Conversation Log</h6>
                      </div>
                      
                      {player.aiInteractions.map((interaction, idx) => (
                        <div key={idx} className="bg-surface-elevated/40 rounded-xl p-4 space-y-3 border border-ai-primary/10">
                          {/* Round Header */}
                          <div className="flex items-center gap-3 pb-2 border-b border-border/20">
                            <div className="flex items-center gap-2">
                              <span className="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-ai-primary/20 text-ai-primary">
                                Round {interaction.round}
                              </span>
                              <span className="text-sm font-medium text-foreground">{interaction.selection}</span>
                            </div>
                          </div>
                          
                          {/* AI Thinking Process */}
                          <div className="space-y-3">
                            <div className="flex items-center gap-2 text-xs text-ai-secondary font-medium">
                              <div className="flex gap-1">
                                <div className="w-1 h-1 bg-ai-primary rounded-full animate-bounce"></div>
                                <div className="w-1 h-1 bg-ai-secondary rounded-full animate-bounce" style={{ animationDelay: '0.2s' }}></div>
                                <div className="w-1 h-1 bg-ai-accent rounded-full animate-bounce" style={{ animationDelay: '0.4s' }}></div>
                              </div>
                              <span>AI Agent Processing...</span>
                            </div>
                            
                            {/* AI Thinking Steps */}
                            {interaction.aiSteps && interaction.aiSteps.length > 0 && (
                              <div className="space-y-2">
                                {interaction.aiSteps.map((step, stepIdx) => (
                                  <div key={stepIdx} className="flex items-start gap-3 p-3 bg-surface/30 rounded-lg border-l-2 border-ai-secondary/30">
                                    <div className="flex-shrink-0 w-6 h-6 rounded-full bg-ai-secondary/20 flex items-center justify-center mt-0.5">
                                      <span className="text-xs">💭</span>
                                    </div>
                                    <div className="flex-1">
                                      <p className="text-sm text-foreground leading-relaxed">{step}</p>
                                    </div>
                                  </div>
                                ))}
                              </div>
                            )}
                            
                            {/* Final AI Response */}
                            <div className="bg-gradient-ai/10 rounded-lg p-4 border border-ai-primary/20 shadow-ai-glow/20">
                              <div className="flex items-start gap-3">
                                <div className="flex-shrink-0 w-8 h-8 rounded-full bg-gradient-ai flex items-center justify-center shadow-glow">
                                  <span className="text-white text-lg">{interaction.aiEmoji}</span>
                                </div>
                                <div className="flex-1">
                                  <div className="flex items-center gap-2 mb-2">
                                    <span className="text-xs font-medium text-ai-primary">AI Agent Response</span>
                                    <div className="h-px bg-gradient-ai flex-1"></div>
                                  </div>
                                  <p className="text-sm text-foreground font-medium leading-relaxed">{interaction.aiThought}</p>
                                </div>
                              </div>
                            </div>
                          </div>
                        </div>
                      ))}
                      
                      <div className="text-center pt-2">
                        <span className="text-xs text-muted-foreground">End of AI conversation log</span>
                      </div>
                    </div>
                  )}
                </div>
              </div>
            );
          })}
        </div>

        {/* Cost Performance Summary */}
        <div className="bg-surface-elevated/30 backdrop-blur-sm rounded-2xl p-6 border border-border/20 animate-fade-in">
          <h3 className="text-lg font-semibold text-foreground mb-4 text-center">
            Final Costs 💰
          </h3>
          <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
            {players.map((player) => (
              <div key={player.id} className="text-center">
                <p className="font-medium text-foreground">{player.name}</p>
                <p className="text-sm text-muted-foreground">
                  Total Spent: ${player.totalCost}
                </p>
                <div className="w-full bg-surface-elevated rounded-full h-2 mt-2">
                  <div 
                    className="bg-gradient-ai h-2 rounded-full transition-all duration-500"
                    style={{ width: `${(player.totalCost / 60) * 100}%` }}
                  />
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Action Buttons */}
        <div className="flex flex-col sm:flex-row gap-4 justify-center animate-fade-in">
          <Button
            onClick={downloadGameData}
            size="lg"
            variant="outline"
            className="px-6 py-6 text-lg border-emerald-400/30 hover:bg-emerald-400/10 transition-all duration-300 text-emerald-400"
          >
            <Download className="w-5 h-5 mr-3" />
            Download JSON
          </Button>
          <Button
            onClick={onShare}
            size="lg"
            variant="outline"
            className="px-8 py-6 text-lg border-ai-primary/30 hover:bg-ai-primary/10 transition-all duration-300"
          >
            <Share2 className="w-5 h-5 mr-3" />
            Share Results
          </Button>
          <Button
            onClick={onPlayAgain}
            size="lg"
            className="px-8 py-6 text-lg bg-gradient-ai hover:shadow-ai-glow transition-all duration-300"
          >
            <RotateCcw className="w-5 h-5 mr-3" />
            New Game
          </Button>
        </div>

        {/* Fun Stats */}
        <div className="text-center space-y-2 text-muted-foreground animate-fade-in">
          <p className="text-sm">
            🎉 {players.length} unique ice cream personalit{players.length > 1 ? 'ies' : 'y'} discovered!
          </p>
          <p className="text-xs">
            Challenge your friends to beat your budget management skills!
          </p>
        </div>
      </div>
    </div>
  );
};