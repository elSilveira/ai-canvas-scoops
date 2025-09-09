import { useState, useEffect } from "react";
import { cn } from "@/lib/utils";
import { Sparkles, Image as ImageIcon, Loader2 } from "lucide-react";
import iceCreamExample from "@/assets/ice-cream-example.jpg";

interface VisualCanvasProps {
  isGenerating: boolean;
  currentPrompt: string | null;
}

export const VisualCanvas = ({ isGenerating, currentPrompt }: VisualCanvasProps) => {
  const [displayImage, setDisplayImage] = useState<string | null>(null);
  const [showPlaceholder, setShowPlaceholder] = useState(true);

  useEffect(() => {
    if (isGenerating && currentPrompt) {
      setDisplayImage(null);
      setShowPlaceholder(false);
      
      // Simulate image generation delay
      setTimeout(() => {
        setDisplayImage(iceCreamExample);
      }, 3000);
    }
  }, [isGenerating, currentPrompt]);

  return (
    <div className="h-full bg-gradient-canvas rounded-xl border border-border/50 p-6">
      {/* Canvas Header */}
      <div className="flex items-center justify-between mb-6">
        <div className="flex items-center gap-3">
          <div className="p-2 rounded-lg bg-gradient-ai">
            <ImageIcon className="w-5 h-5 text-white" />
          </div>
          <div>
            <h2 className="text-xl font-semibold text-foreground">Visual Canvas</h2>
            <p className="text-sm text-muted-foreground">Your creations appear here</p>
          </div>
        </div>
        {isGenerating && (
          <div className="flex items-center gap-2 text-ai-primary">
            <Loader2 className="w-4 h-4 animate-spin" />
            <span className="text-sm font-medium">Generating...</span>
          </div>
        )}
      </div>

      {/* Canvas Area */}
      <div className="relative w-full h-[calc(100%-5rem)] bg-surface/30 rounded-lg border border-border/30 overflow-hidden">
        {showPlaceholder && !isGenerating && !displayImage && (
          <div className="absolute inset-0 flex items-center justify-center">
            <div className="text-center space-y-4">
              <div className="p-4 rounded-full bg-gradient-glow mx-auto w-fit">
                <Sparkles className="w-12 h-12 text-ai-primary animate-pulse-glow" />
              </div>
              <div className="space-y-2">
                <h3 className="text-lg font-medium text-foreground">Ready to Create</h3>
                <p className="text-muted-foreground max-w-md">
                  Start a conversation in the chat to generate amazing AI creations
                </p>
              </div>
            </div>
          </div>
        )}

        {isGenerating && (
          <div className="absolute inset-0 flex items-center justify-center bg-surface/50">
            <div className="text-center space-y-6">
              <div className="relative">
                <div className="p-6 rounded-full bg-gradient-ai mx-auto w-fit animate-pulse-glow">
                  <Sparkles className="w-16 h-16 text-white animate-spin" />
                </div>
                <div className="absolute inset-0 bg-gradient-glow rounded-full animate-ping opacity-30"></div>
              </div>
              <div className="space-y-2">
                <h3 className="text-xl font-semibold text-foreground">Creating Magic</h3>
                <p className="text-muted-foreground max-w-md">
                  "{currentPrompt}"
                </p>
                <div className="flex items-center justify-center gap-2 mt-4">
                  <div className="w-2 h-2 bg-ai-primary rounded-full animate-bounce"></div>
                  <div className="w-2 h-2 bg-ai-secondary rounded-full animate-bounce" style={{ animationDelay: '0.1s' }}></div>
                  <div className="w-2 h-2 bg-ai-accent rounded-full animate-bounce" style={{ animationDelay: '0.2s' }}></div>
                </div>
              </div>
            </div>
          </div>
        )}

        {displayImage && !isGenerating && (
          <div className="absolute inset-0 p-4">
            <div className="relative w-full h-full rounded-lg overflow-hidden bg-white shadow-glow animate-scale-in">
              <img
                src={displayImage}
                alt="AI Generated Creation"
                className="w-full h-full object-contain"
              />
              <div className="absolute top-4 left-4">
                <div className="bg-gradient-ai text-white px-3 py-1 rounded-full text-sm font-medium">
                  Fresh Creation
                </div>
              </div>
            </div>
          </div>
        )}

        {/* Ambient particles effect */}
        <div className="absolute inset-0 pointer-events-none">
          <div className="absolute top-1/4 left-1/4 w-2 h-2 bg-ai-primary/20 rounded-full animate-ping" style={{ animationDelay: '0s' }}></div>
          <div className="absolute top-3/4 right-1/3 w-1 h-1 bg-ai-secondary/30 rounded-full animate-ping" style={{ animationDelay: '1s' }}></div>
          <div className="absolute bottom-1/4 left-1/2 w-1 h-1 bg-ai-accent/25 rounded-full animate-ping" style={{ animationDelay: '2s' }}></div>
        </div>
      </div>
    </div>
  );
};