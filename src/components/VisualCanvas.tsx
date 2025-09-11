import { useState, useEffect } from "react";
import { cn } from "@/lib/utils";
import { Sparkles, Image as ImageIcon, Loader2 } from "lucide-react";
import iceCreamExample from "@/assets/ice-cream-example.jpg";
import { apiService } from "@/services/api";

interface VisualCanvasProps {
  isGenerating: boolean;
  currentPrompt: string | null;
  playerSelections?: string[];
  playerName?: string;
  onImageGenerated?: (imageUrl: string) => void;
}

export const VisualCanvas = ({ 
  isGenerating, 
  currentPrompt, 
  playerSelections, 
  playerName,
  onImageGenerated 
}: VisualCanvasProps) => {
  const [displayImage, setDisplayImage] = useState<string | null>(null);
  const [showPlaceholder, setShowPlaceholder] = useState(true);
  const [imageError, setImageError] = useState<string | null>(null);
  const [generationProgress, setGenerationProgress] = useState<string>("");
  const [imageCache, setImageCache] = useState<Map<string, string>>(new Map());
  const [generationAttempts, setGenerationAttempts] = useState(0);
  const [estimatedTime, setEstimatedTime] = useState<number>(0);

  useEffect(() => {
    if (isGenerating && currentPrompt && playerSelections && playerName) {
      setDisplayImage(null);
      setShowPlaceholder(false);
      setImageError(null);
      setGenerationAttempts(prev => prev + 1);
      
      // Create cache key from selections
      const cacheKey = `${playerName}-${playerSelections.filter(s => s !== 'Skip').sort().join('-')}`;
      
      // Check cache first
      if (imageCache.has(cacheKey)) {
        console.log("🎯 Using cached image for", playerName);
        setGenerationProgress("Loading from cache...");
        setTimeout(() => {
          const cachedImage = imageCache.get(cacheKey)!;
          setDisplayImage(cachedImage);
          onImageGenerated?.(cachedImage);
          setGenerationProgress("Image loaded from cache!");
        }, 500);
        return;
      }
      
      // Start generation timer
      const startTime = Date.now();
      setEstimatedTime(8); // Estimate 8 seconds
      
      // Update progress with countdown
      const progressInterval = setInterval(() => {
        const elapsed = (Date.now() - startTime) / 1000;
        const remaining = Math.max(0, estimatedTime - elapsed);
        if (remaining > 0) {
          setGenerationProgress(`Generating image... ~${Math.ceil(remaining)}s remaining`);
        }
      }, 1000);
      
      // Generate image using backend API with enhanced progress tracking
      const generateImageWithProgress = async () => {
        try {
          setGenerationProgress("🎨 Connecting to AI image generator...");
          
          // Progressive updates for better UX
          const progressUpdates = [
            "🤖 AI analyzing your selections...",
            "🎯 Creating unique ice cream design...",
            "🎨 Generating high-quality image...",
            "✨ Adding final touches..."
          ];
          
          for (let i = 0; i < progressUpdates.length; i++) {
            setTimeout(() => {
              setGenerationProgress(progressUpdates[i]);
            }, i * 1500);
          }
          
          const result = await apiService.generateIceCreamImage(
            playerSelections,
            playerName,
            'realistic',
            '1024x1024'
          );
          
          clearInterval(progressInterval);
          
          if (result.success && result.imageUrl) {
            setGenerationProgress("🎉 Image generated successfully!");
            setDisplayImage(result.imageUrl);
            
            // Cache the successful result
            setImageCache(prev => new Map(prev).set(cacheKey, result.imageUrl!));
            
            onImageGenerated?.(result.imageUrl);
            
            console.log("✅ Image generation successful:", {
              player: playerName,
              attempts: generationAttempts,
              cached: true
            });
          } else {
            throw new Error(result.error || "Image generation failed");
          }
          
        } catch (error) {
          clearInterval(progressInterval);
          console.error("❌ Image generation failed:", error);
          
          const errorMessage = error instanceof Error ? error.message : "Failed to generate image";
          setImageError(errorMessage);
          
          // Progressive fallback messages
          setGenerationProgress("⚠️ Generation failed, switching to fallback...");
          
          setTimeout(() => {
            setGenerationProgress("🔄 Using example image...");
            setTimeout(() => {
              setDisplayImage(iceCreamExample);
              onImageGenerated?.(iceCreamExample);
              setGenerationProgress("✅ Fallback image loaded");
            }, 1000);
          }, 1500);
        }
      };
      
      generateImageWithProgress();
      
      // Cleanup
      return () => {
        clearInterval(progressInterval);
      };
    }
  }, [isGenerating, currentPrompt, playerSelections, playerName, onImageGenerated, imageCache, generationAttempts, estimatedTime]);

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
          <div className="absolute inset-0 flex items-center justify-center bg-surface/50 backdrop-blur-sm">
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
                {generationProgress && (
                  <div className="space-y-2">
                    <p className="text-sm text-ai-primary font-medium">
                      {generationProgress}
                    </p>
                    {/* Progress indicator for long operations */}
                    {generationProgress.includes('remaining') && (
                      <div className="w-48 mx-auto bg-surface/30 rounded-full h-1">
                        <div className="bg-gradient-to-r from-ai-primary to-ai-secondary h-1 rounded-full animate-pulse" />
                      </div>
                    )}
                  </div>
                )}
                {imageError && (
                  <div className="mt-3 p-2 bg-yellow-500/10 border border-yellow-500/20 rounded-lg">
                    <p className="text-sm text-yellow-600">
                      ⚠️ {imageError}
                    </p>
                    <p className="text-xs text-muted-foreground mt-1">
                      Switching to fallback mode...
                    </p>
                  </div>
                )}
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
                onLoad={() => console.log("✅ Image loaded successfully")}
                onError={() => setImageError("Failed to load generated image")}
              />
              <div className="absolute top-4 left-4">
                <div className="bg-gradient-ai text-white px-3 py-1 rounded-full text-sm font-medium">
                  {imageCache.has(`${playerName}-${playerSelections?.filter(s => s !== 'Skip').sort().join('-')}`) ? 
                    "🎯 Cached Creation" : "✨ Fresh Creation"
                  }
                </div>
              </div>
              <div className="absolute top-4 right-4">
                <div className="bg-black/20 text-white px-2 py-1 rounded text-xs">
                  For {playerName}
                </div>
              </div>
              <div className="absolute bottom-4 left-4 right-4">
                <div className="bg-black/40 backdrop-blur-sm text-white p-3 rounded-lg">
                  <p className="text-sm font-medium">🍦 AI-Generated Ice Cream</p>
                  <p className="text-xs opacity-90">
                    Based on: {playerSelections?.filter(s => s !== 'Skip').join(', ') || 'Player selections'}
                  </p>
                  {generationAttempts > 1 && (
                    <p className="text-xs opacity-75 mt-1">
                      Generation attempt #{generationAttempts}
                    </p>
                  )}
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