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

interface FinalRevealProps {
  personality: IceCreamPersonality;
  selections: string[];
  onPlayAgain: () => void;
  onShare: () => void;
}

export const FinalReveal = ({ 
  personality, 
  selections, 
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
      <div className="max-w-4xl mx-auto w-full space-y-8">
        {/* Celebration Header */}
        <div className="text-center space-y-4 animate-fade-in">
          <div className="flex items-center justify-center gap-2 text-ai-primary">
            <Sparkles className="w-6 h-6" />
            <span className="text-lg font-semibold">Your Perfect Match</span>
            <Sparkles className="w-6 h-6" />
          </div>
          <h1 className="text-4xl md:text-5xl font-bold text-foreground">
            Meet Your Ice Cream Twin!
          </h1>
        </div>

        {/* Ice Cream Reveal */}
        <div className={`transition-all duration-1000 ${isRevealed ? 'animate-scale-in' : 'scale-50 opacity-0'}`}>
          <div className="bg-surface-elevated/50 backdrop-blur-sm rounded-3xl p-8 border border-border/30 shadow-ai-glow">
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-8 items-center">
              {/* Ice Cream Visual */}
              <div className="text-center space-y-6">
                <div 
                  className="mx-auto w-48 h-48 rounded-full flex items-center justify-center text-8xl animate-bounce shadow-glow"
                  style={{ 
                    background: personality.gradient,
                    boxShadow: `0 0 50px ${personality.color}40`
                  }}
                >
                  {personality.emoji}
                </div>
                <div className="space-y-2">
                  <h2 className="text-3xl font-bold bg-gradient-ai bg-clip-text text-transparent">
                    {personality.name}
                  </h2>
                  <p className="text-muted-foreground text-lg">
                    {personality.description}
                  </p>
                </div>
              </div>

              {/* Personality Insights */}
              <div className="space-y-6">
                <h3 className="text-xl font-semibold text-foreground">
                  What This Says About You:
                </h3>
                <div className="space-y-4">
                  {personality.insights.map((insight, index) => (
                    <div 
                      key={index}
                      className="flex items-start gap-3 animate-fade-in"
                      style={{ animationDelay: `${index * 0.2}s` }}
                    >
                      <div className="p-1 rounded-full bg-ai-primary/20 mt-1">
                        <Sparkles className="w-3 h-3 text-ai-primary" />
                      </div>
                      <p className="text-foreground">{insight}</p>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* Your Journey */}
        <div className="bg-surface-elevated/30 backdrop-blur-sm rounded-2xl p-6 border border-border/20 animate-fade-in">
          <h3 className="text-lg font-semibold text-foreground mb-4 text-center">
            Your Flavor Journey
          </h3>
          <div className="flex flex-wrap justify-center gap-3">
            {selections.map((selection, index) => (
              <div 
                key={index}
                className="px-4 py-2 bg-gradient-ai/10 rounded-full text-sm text-foreground border border-ai-primary/20"
              >
                {selection}
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
            Share Your Flavor
          </Button>
          <Button
            onClick={onPlayAgain}
            size="lg"
            className="px-8 py-6 text-lg bg-gradient-ai hover:shadow-ai-glow transition-all duration-300"
          >
            <RotateCcw className="w-5 h-5 mr-3" />
            Play Again
          </Button>
        </div>

        {/* Fun Stats */}
        <div className="text-center space-y-2 text-muted-foreground animate-fade-in">
          <p className="text-sm">
            🎉 You're one of the unique flavors in our ice cream universe!
          </p>
          <p className="text-xs">
            Share with friends to see what flavors they discover
          </p>
        </div>
      </div>
    </div>
  );
};