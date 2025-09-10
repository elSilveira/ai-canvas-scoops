import { Button } from "@/components/ui/button";
import { Share2, RotateCcw, Sparkles, Download, MessageSquare } from "lucide-react";
import { useState, useEffect } from "react";

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
}

interface Player {
  id: string;
  name: string;
  selections: string[];
  totalCost: number;
  aiInteractions: AIInteraction[];
}

interface FinalRevealProps {
  players: Player[];
  generatePersonality: (selections: string[]) => IceCreamPersonality;
  onPlayAgain: () => void;
  onShare: () => void;
}

export const FinalReveal = ({ 
  players,
  generatePersonality,
  onPlayAgain, 
  onShare 
}: FinalRevealProps) => {
  const [isRevealed, setIsRevealed] = useState(false);
  const [showInteractions, setShowInteractions] = useState<string | null>(null);

  useEffect(() => {
    const timer = setTimeout(() => {
      setIsRevealed(true);
    }, 500);
    return () => clearTimeout(timer);
  }, []);

  const downloadGameData = () => {
    const gameData = {
      gameDate: new Date().toISOString(),
      players: players.map(player => ({
        ...player,
        personality: generatePersonality(player.selections),
        aiInteractions: player.aiInteractions
      })),
      totalPlayers: players.length,
      gameVersion: "1.0"
    };

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
                      <div 
                        className="mx-auto w-32 h-32 rounded-full flex items-center justify-center text-5xl shadow-glow animate-bounce"
                        style={{ 
                          background: personality.gradient,
                          boxShadow: `0 0 30px ${personality.color}40`
                        }}
                      >
                        {personality.emoji}
                      </div>
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

                  {/* Player's Selections */}
                  <div className="mb-4">
                    <h5 className={`text-sm font-semibold mb-2 text-center ${
                      isEmptyPlayer ? 'text-slate-600 dark:text-slate-400' : 'text-foreground'
                    }`}>
                      {isEmptyPlayer ? 'Skip Journey' : 'Flavor Journey'}
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