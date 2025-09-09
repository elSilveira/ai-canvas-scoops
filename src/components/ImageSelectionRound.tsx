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
  currentRound: number;
  totalRounds: number;
}

export const ImageSelectionRound = ({ 
  round, 
  onSelect, 
  currentRound, 
  totalRounds 
}: ImageSelectionRoundProps) => {
  const [selectedChoice, setSelectedChoice] = useState<ImageChoice | null>(null);
  const [isSelecting, setIsSelecting] = useState(false);

  const handleSelect = (choice: ImageChoice) => {
    if (isSelecting) return;
    
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
        {/* Progress */}
        <div className="text-center space-y-4">
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
          <p className="text-sm font-medium text-ai-primary uppercase tracking-wider">
            {round.category}
          </p>
          <h2 className="text-3xl md:text-4xl font-bold text-foreground">
            {round.question}
          </h2>
        </div>

        {/* Image Choices */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 animate-fade-in">
          {round.choices.map((choice, index) => (
            <Button
              key={choice.id}
              onClick={() => handleSelect(choice)}
              variant="ghost"
              className={cn(
                "h-auto p-0 group relative overflow-hidden rounded-2xl transition-all duration-300",
                "hover:scale-105 hover:shadow-glow",
                selectedChoice?.id === choice.id && "ring-4 ring-ai-primary scale-105",
                isSelecting && selectedChoice?.id !== choice.id && "opacity-50 scale-95"
              )}
              style={{ animationDelay: `${index * 0.1}s` }}
              disabled={isSelecting}
            >
              <div className="relative aspect-[4/3] w-full overflow-hidden rounded-2xl">
                <img
                  src={choice.image}
                  alt={choice.title}
                  className="w-full h-full object-cover transition-transform duration-300 group-hover:scale-110"
                />
                <div className="absolute inset-0 bg-gradient-to-t from-black/60 via-transparent to-transparent" />
                
                {/* Content */}
                <div className="absolute bottom-0 left-0 right-0 p-6 text-left">
                  <h3 className="font-bold text-white text-xl mb-2">
                    {choice.title}
                  </h3>
                  <p className="text-white/90 text-sm">
                    {choice.description}
                  </p>
                </div>

                {/* Selection Indicator */}
                {selectedChoice?.id === choice.id && (
                  <div className="absolute inset-0 bg-ai-primary/20 flex items-center justify-center">
                    <div className="bg-ai-primary text-white px-4 py-2 rounded-full font-semibold animate-scale-in">
                      Selected!
                    </div>
                  </div>
                )}
              </div>
            </Button>
          ))}
        </div>
      </div>
    </div>
  );
};