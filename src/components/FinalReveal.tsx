import { Button } from "@/components/ui/button";
import { Share2, RotateCcw, Sparkles } from "lucide-react";
import { useState, useEffect } from "react";

export interface IceCreamPersonality {
  name: string;
  emoji: string;
  description: string;
  insights: string[];
  color: string;
  gradient: string;
}

interface Player {
  id: string;
  name: string;
  selections: string[];
  totalCost: number;
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

  useEffect(() => {
    const timer = setTimeout(() => {
      setIsRevealed(true);
    }, 500);
    return () => clearTimeout(timer);
  }, []);

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
          
          return (
              <div 
                key={player.id}
                className="bg-surface-elevated/50 backdrop-blur-sm rounded-3xl p-6 border border-border/30 shadow-ai-glow"
                style={{ animationDelay: `${index * 0.2}s` }}
              >
                {/* Player Name & Cost */}
                <div className="space-y-4">
                  <div className="flex items-center justify-between">
                    <h3 className="text-xl font-bold text-foreground">{player.name}</h3>
                    <span className="text-lg font-semibold text-emerald-400">
                      Total Cost: ${player.totalCost}
                    </span>
                  </div>

                  {/* Ice Cream Visual */}
                  <div className="text-center space-y-4 mb-6">
                    <div 
                      className="mx-auto w-32 h-32 rounded-full flex items-center justify-center text-5xl animate-bounce shadow-glow"
                      style={{ 
                        background: personality.gradient,
                        boxShadow: `0 0 30px ${personality.color}40`
                      }}
                    >
                      {personality.emoji}
                    </div>
                    <div className="space-y-2">
                      <h4 className="text-lg font-bold bg-gradient-ai bg-clip-text text-transparent">
                        {personality.name}
                      </h4>
                      <p className="text-muted-foreground text-sm">
                        {personality.description}
                      </p>
                    </div>
                  </div>

                  {/* Player's Selections */}
                  <div className="mb-4">
                    <h5 className="text-sm font-semibold text-foreground mb-2 text-center">
                      Flavor Journey
                    </h5>
                    <div className="flex flex-wrap justify-center gap-2">
                      {player.selections.map((selection, selIndex) => (
                        <div 
                          key={selIndex}
                          className="px-2 py-1 bg-gradient-ai/10 rounded-full text-xs text-foreground border border-ai-primary/20"
                        >
                          {selection}
                        </div>
                      ))}
                    </div>
                  </div>

                  {/* Key Insight */}
                  <div className="text-center">
                    <div className="flex items-start justify-center gap-2">
                      <div className="p-1 rounded-full bg-ai-primary/20 mt-0.5">
                        <Sparkles className="w-3 h-3 text-ai-primary" />
                      </div>
                      <p className="text-sm text-foreground text-center">
                        {personality.insights[0]}
                      </p>
                    </div>
                  </div>
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