import { Brain, Sparkles } from "lucide-react";
import { useEffect, useState } from "react";
import { apiService, type PlayerGameData } from "@/services/api";

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
  playerData: PlayerGameData;
  onComplete: (result: any) => void;
  duration?: number;
  // Keep conversation as optional for backward compatibility
  conversation?: ThinkingConversation;
}

export const AIThinkingScreen = ({ 
  playerData,
  onComplete, 
  duration = 6000,
  conversation 
}: AIThinkingScreenProps) => {
  const [currentPhase, setCurrentPhase] = useState(0);
  const [processingResult, setProcessingResult] = useState<any>(null);
  const [error, setError] = useState<string | null>(null);
  const [realTimeSteps, setRealTimeSteps] = useState<string[]>([]);
  const [processingProgress, setProcessingProgress] = useState(0);
  const [isProcessingComplete, setIsProcessingComplete] = useState(false);
  
  // Use real-time steps if available, otherwise fall back to conversation
  const phases = realTimeSteps.length > 0 ? realTimeSteps : 
    conversation ? [
      ...conversation.steps.map(step => step.text),
      conversation.finalResponse.text
    ] : [
      "Connecting to AI processing system...",
      "Analyzing your selections...",
      "Processing through AI agents...",
      "Finalizing your personalized result..."
    ];
  
  const phaseEmojis = conversation ? [
    ...conversation.steps.map(step => step.emoji),
    conversation.finalResponse.emoji
  ] : ['🔗', '🔍', '🤖', '✨'];

  // Process player data with backend when component mounts
  useEffect(() => {
    const processPlayerDataRealTime = async () => {
      try {
        console.log("🎮 Starting real-time AI processing for player:", playerData.name);
        
        // Initialize with connecting step
        setRealTimeSteps(["🔗 Connecting to AI processing system..."]);
        
        // Simulate progressive updates for better UX
        const progressSteps = [
          "🔗 Connected to AI processing system",
          "🔍 Analyzing player selections...",
          "🤖 Processing through AI orchestrator...",
          "💫 Mapping selections to ingredients...",
          "💰 Calculating precise costs...",
          "✨ Finalizing recommendations..."
        ];
        
        // Add steps progressively with delays for real-time feel
        for (let i = 0; i < progressSteps.length; i++) {
          await new Promise(resolve => setTimeout(resolve, 800));
          setRealTimeSteps(prev => [...prev.slice(0, 1), ...progressSteps.slice(0, i + 1)]);
        }
        
        // Call the backend API
        const result = await apiService.processPlayerGame(playerData, {
          generateImage: false, // Don't generate images during thinking phase
          verbose: true,
          qualityLevel: 'balanced'
        });
        
        if (result.success) {
          // Update with actual backend reasoning
          const backendSteps = result.data.aiReasoningSteps || [];
          const finalSteps = [
            "🔗 Connected to AI processing system",
            "🔍 Analysis complete",
            ...backendSteps.map((step, index) => {
              const emojis = ['🧠', '⚙️', '🎯', '💡', '✨', '🔥'];
              return `${emojis[index % emojis.length]} ${step}`;
            }),
            "👍 Recommendations ready!",
            "✅ Processing complete!"
          ];
          
          setRealTimeSteps(finalSteps);
          setProcessingResult(result.data);
          console.log("✅ Real-time AI processing completed successfully");
        } else {
          throw new Error(result.error || "Processing failed");
        }
        
      } catch (err) {
        console.error("❌ Real-time AI processing failed:", err);
        setError(err instanceof Error ? err.message : "Processing failed");
        
        // Enhanced fallback with better messaging
        setRealTimeSteps([
          "🔗 Connection established",
          "⚠️ AI services temporarily unavailable",
          "🔄 Switching to offline processing mode",
          "🧠 Analyzing selections locally...",
          "💰 Calculating estimated costs...",
          "✅ Fallback processing complete"
        ]);
        
        // Create fallback result
        const fallbackResult = {
          estimatedCost: playerData.selections.filter(s => s !== 'Skip').length * 12.5,
          ingredientsUsed: playerData.selections.filter(s => s !== 'Skip'),
          aiReasoningSteps: [
            "Processed selections in offline mode",
            "Applied standard cost calculation",
            "Generated basic personality profile"
          ]
        };
        setProcessingResult({ data: fallbackResult });
      }
    };
    
    processPlayerDataRealTime();
  }, [playerData]);

  useEffect(() => {
    const phaseInterval = setInterval(() => {
      setCurrentPhase(prev => {
        if (prev < phases.length - 1) {
          const nextPhase = prev + 1;
          setProcessingProgress((nextPhase / phases.length) * 100);
          return nextPhase;
        }
        return prev;
      });
    }, duration / phases.length);

    const completeTimer = setTimeout(() => {
      clearInterval(phaseInterval);
      setIsProcessingComplete(true);
      setProcessingProgress(100);
      
      // Small delay before calling onComplete for better UX
      setTimeout(() => {
        // Pass the processing result to onComplete
        onComplete(processingResult || { error });
      }, 1000);
    }, duration);

    return () => {
      clearInterval(phaseInterval);
      clearTimeout(completeTimer);
    };
  }, [duration, phases.length, processingResult, error]);

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
            AI is thinking about {playerData.name}'s perfect ice cream...
          </h2>
          
          {/* Progress Bar */}
          <div className="w-full max-w-md mx-auto">
            <div className="flex justify-between text-sm text-muted-foreground mb-2">
              <span>Processing...</span>
              <span>{Math.round(processingProgress)}%</span>
            </div>
            <div className="w-full bg-surface/30 rounded-full h-2">
              <div 
                className="bg-gradient-to-r from-ai-primary to-ai-secondary h-2 rounded-full transition-all duration-500 ease-out"
                style={{ width: `${processingProgress}%` }}
              />
            </div>
          </div>
          
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
            
            {/* Error Display */}
            {error && (
              <div className="mt-4 p-3 bg-yellow-500/10 border border-yellow-500/20 rounded-lg">
                <p className="text-yellow-600 text-sm">⚠️ {error}</p>
                <p className="text-xs text-muted-foreground mt-1">Continuing with fallback processing...</p>
              </div>
            )}
            
            {/* Completion Status */}
            {isProcessingComplete && (
              <div className="mt-4 p-3 bg-green-500/10 border border-green-500/20 rounded-lg">
                <p className="text-green-600 text-sm">✅ Processing complete! Preparing results...</p>
              </div>
            )}
            
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