import { Brain, Sparkles } from "lucide-react";
import { useEffect, useState } from "react";

export interface ThinkingStep {
  text: string;
  emoji: string;
  type: 'analyzing' | 'considering' | 'connecting' | 'concluding';
}

export interface ThinkingConversation {
  steps: ThinkingStep[];
  finalResponse: {
    text: string;
    emoji: string;
  };
}

interface AIThinkingScreenProps {
  conversation: ThinkingConversation;
  onComplete: () => void;
  duration?: number;
}

export const AIThinkingScreen = ({ 
  conversation, 
  onComplete, 
  duration = 4000 
}: AIThinkingScreenProps) => {
  const [currentPhase, setCurrentPhase] = useState(0);
  
  // Create phases from conversation steps plus final response
  const phases = [
    ...conversation.steps.map(step => step.text),
    conversation.finalResponse.text
  ];
  
  const phaseEmojis = [
    ...conversation.steps.map(step => step.emoji),
    conversation.finalResponse.emoji
  ];

  useEffect(() => {
    const phaseInterval = setInterval(() => {
      setCurrentPhase(prev => {
        if (prev < phases.length - 1) {
          return prev + 1;
        }
        return prev;
      });
    }, duration / phases.length);

    const completeTimer = setTimeout(() => {
      onComplete();
    }, duration);

    return () => {
      clearInterval(phaseInterval);
      clearTimeout(completeTimer);
    };
  }, [duration, onComplete, phases.length]);

  return (
    <div className="min-h-screen bg-gradient-canvas flex items-center justify-center p-6">
      <div className="text-center max-w-2xl mx-auto space-y-8">
        {/* AI Brain Animation */}
        <div className="relative mx-auto w-fit">
          <div className="p-8 rounded-full bg-gradient-ai shadow-ai-glow animate-pulse-glow">
            <Brain className="w-20 h-20 text-white animate-pulse" />
          </div>
          
          {/* Floating particles */}
          <div className="absolute -top-4 -left-4 p-2 rounded-full bg-ai-secondary/30 animate-bounce">
            <Sparkles className="w-4 h-4 text-ai-secondary" />
          </div>
          <div className="absolute -bottom-2 -right-6 p-2 rounded-full bg-ai-accent/30 animate-bounce" style={{ animationDelay: '0.5s' }}>
            <Sparkles className="w-3 h-3 text-ai-accent" />
          </div>
          <div className="absolute top-0 -right-2 p-2 rounded-full bg-ai-primary/30 animate-bounce" style={{ animationDelay: '1s' }}>
            <Sparkles className="w-4 h-4 text-ai-primary" />
          </div>

          {/* Pulsing rings */}
          <div className="absolute inset-0 bg-gradient-glow rounded-full animate-ping opacity-30"></div>
          <div className="absolute inset-0 bg-gradient-glow rounded-full animate-ping opacity-20" style={{ animationDelay: '0.5s' }}></div>
        </div>

        {/* AI Thinking Text */}
        <div className="space-y-6">
          <h2 className="text-2xl font-semibold text-foreground animate-fade-in">
            AI is thinking...
          </h2>
          
          <div className="bg-surface-elevated/50 backdrop-blur-sm rounded-2xl p-6 border border-border/30">
            <div className="flex items-center justify-center gap-3 mb-4">
              <div className="flex gap-1">
                <div className="w-2 h-2 bg-ai-primary rounded-full animate-bounce"></div>
                <div className="w-2 h-2 bg-ai-secondary rounded-full animate-bounce" style={{ animationDelay: '0.2s' }}></div>
                <div className="w-2 h-2 bg-ai-accent rounded-full animate-bounce" style={{ animationDelay: '0.4s' }}></div>
              </div>
            </div>
            
            <p className="text-lg text-foreground transition-all duration-500 animate-fade-in" key={currentPhase}>
              {phases[currentPhase]}
            </p>
            
            <div className="mt-4 text-4xl animate-bounce">
              {phaseEmojis[currentPhase]}
            </div>
          </div>
        </div>

        {/* Progress dots */}
        <div className="flex justify-center gap-2">
          {phases.map((_, index) => (
            <div
              key={index}
              className={`w-2 h-2 rounded-full transition-all duration-300 ${
                index <= currentPhase ? 'bg-ai-primary' : 'bg-surface-elevated'
              }`}
            />
          ))}
        </div>
      </div>
    </div>
  );
};