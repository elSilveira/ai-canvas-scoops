import { Button } from "@/components/ui/button";
import { cn } from "@/lib/utils";
import { useState } from "react";

export interface ImageChoice {
  id: string;
  image: string;
  title: string;
  description: string;
  value: string;
}

export interface Round {
  id: string;
  category: string;
  question: string;
  choices: ImageChoice[];
}

interface ImageSelectionRoundProps {
  round: Round;
  onSelect: (choice: ImageChoice) => void;
  onSkip: () => void;
  currentRound: number;
  totalRounds: number;
  player: {
    id: string;
    name: string;
    selections: string[];
    totalCost: number;
  };
  inventory: {
    [key: string]: {
      available: number;
      price: number;
    };
  };
}

export const ImageSelectionRound = ({ 
  round, 
  onSelect, 
  onSkip,
  currentRound, 
  totalRounds,
  player,
  inventory
}: ImageSelectionRoundProps) => {
  const [selectedChoice, setSelectedChoice] = useState<ImageChoice | null>(null);
  const [isSelecting, setIsSelecting] = useState(false);

  const isAvailable = (choice: ImageChoice): boolean => {
    const ingredient = inventory[choice.value];
    return ingredient && ingredient.available > 0;
  };

  const handleSelect = (choice: ImageChoice) => {
    if (isSelecting || !isAvailable(choice)) return;
    
    setSelectedChoice(choice);
    setIsSelecting(true);
    
    // Brief delay for visual feedback
    setTimeout(() => {
      onSelect(choice);
    }, 600);
  };

  return (
    <div className="min-h-screen bg-gradient-canvas p-6 flex items-center justify-center">
      <div className="max-w-5xl mx-auto w-full space-y-8">
        {/* Player Info & Progress */}
        <div className="text-center space-y-4">
          <div className="bg-surface-elevated p-4 rounded-xl border border-surface-border">
            <h3 className="text-xl font-bold text-ai-primary">{player.name}'s Turn</h3>
          </div>
          <div className="flex items-center justify-center gap-2">
            <span className="text-sm font-medium text-muted-foreground">
              Round {currentRound} of {totalRounds}
            </span>
          </div>
          <div className="w-full max-w-md mx-auto bg-surface-elevated rounded-full h-2">
            <div 
              className="bg-gradient-ai h-2 rounded-full transition-all duration-500"
              style={{ width: `${(currentRound / totalRounds) * 100}%` }}
            />
          </div>
        </div>

        {/* Question */}
        <div className="text-center space-y-2 animate-fade-in">
          <h2 className="text-3xl md:text-4xl font-bold text-foreground">
            {round.question}
          </h2>
        </div>

        {/* Skip Button */}
        <div className="flex justify-center mb-4">
          <Button
            onClick={onSkip}
            variant="outline"
            className="text-xs px-3 py-1 opacity-50 hover:opacity-100 transition-opacity duration-300 border-dashed"
            disabled={isSelecting}
          >
            🙈 Skip this round
          </Button>
        </div>

        {/* Image Choices */}
        <div className="flex justify-center">
          <div className="grid grid-cols-2 gap-6 w-fit animate-fade-in">
            {round.choices.map((choice, index) => {
              const ingredient = inventory[choice.value];
              const available = ingredient?.available > 0;
              
              return (
                <Button
                  key={choice.id}
                  onClick={() => handleSelect(choice)}
                  variant="ghost"
                  className={cn(
                    "h-auto p-0 group relative overflow-hidden rounded-2xl transition-all duration-300",
                    available && "hover:scale-105 hover:shadow-glow",
                    !available && "opacity-30 cursor-not-allowed grayscale",
                    selectedChoice?.id === choice.id && "ring-4 ring-ai-primary scale-105",
                    isSelecting && selectedChoice?.id !== choice.id && "opacity-50 scale-95"
                  )}
                  style={{ animationDelay: `${index * 0.1}s` }}
                  disabled={isSelecting || !available}
                >
                  <div className="relative aspect-[4/3] w-80 overflow-hidden rounded-2xl">
                    <img
                      src={choice.image}
                      alt="Choice option"
                      className="w-full h-full object-cover transition-transform duration-300 group-hover:scale-110"
                    />

                    {/* Availability Overlay */}
                    <div className="absolute top-3 right-3">
                      <div className={cn(
                        "px-3 py-1 rounded-full text-sm font-bold",
                        ingredient?.available > 0 ? "bg-emerald-500 text-white" : "bg-red-500 text-white"
                      )}>
                        {ingredient?.available || 0} left
                      </div>
                    </div>

                    {/* Selection Indicator */}
                    {selectedChoice?.id === choice.id && (
                      <div className="absolute inset-0 bg-ai-primary/20 flex items-center justify-center">
                        <div className="bg-ai-primary text-white px-4 py-2 rounded-full font-semibold animate-scale-in">
                          Selected!
                        </div>
                      </div>
                    )}

                    {/* Out of Stock Overlay */}
                    {!available && (
                      <div className="absolute inset-0 bg-black/60 flex items-center justify-center">
                        <div className="bg-red-500 text-white px-4 py-2 rounded-full font-semibold">
                          Sold Out
                        </div>
                      </div>
                    )}
                  </div>
                </Button>
              );
            })}
          </div>
        </div>
      </div>
    </div>
  );
};