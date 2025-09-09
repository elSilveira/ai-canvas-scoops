import { Button } from "@/components/ui/button";
import { Sparkles, IceCream } from "lucide-react";

interface WelcomeScreenProps {
  onStartGame: () => void;
}

export const WelcomeScreen = ({ onStartGame }: WelcomeScreenProps) => {
  return (
    <div className="flex items-center justify-center min-h-screen bg-gradient-canvas p-6">
      <div className="text-center max-w-2xl mx-auto space-y-8 animate-fade-in">
        {/* Hero Icon */}
        <div className="relative mx-auto w-fit">
          <div className="p-8 rounded-full bg-gradient-ai shadow-ai-glow">
            <IceCream className="w-20 h-20 text-white" />
          </div>
          <div className="absolute -top-2 -right-2 p-2 rounded-full bg-ai-accent animate-bounce">
            <Sparkles className="w-6 h-6 text-white" />
          </div>
        </div>

        {/* Headlines */}
        <div className="space-y-4">
          <h1 className="text-5xl md:text-6xl font-bold bg-gradient-ai bg-clip-text text-transparent">
            Which Ice Cream Are You?
          </h1>
          <p className="text-xl text-muted-foreground leading-relaxed">
            Pick the images that match your vibe — from action movies to sweet toppings — 
            and let our AI scoop out your perfect flavor.
          </p>
        </div>

        {/* Features */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 text-center">
          <div className="space-y-3">
            <div className="p-3 rounded-lg bg-ai-primary/10 mx-auto w-fit">
              <Sparkles className="w-6 h-6 text-ai-primary" />
            </div>
            <h3 className="font-semibold text-foreground">Fun Choices</h3>
            <p className="text-sm text-muted-foreground">
              Pick between themed images that match your personality
            </p>
          </div>
          <div className="space-y-3">
            <div className="p-3 rounded-lg bg-ai-secondary/10 mx-auto w-fit">
              <IceCream className="w-6 h-6 text-ai-secondary" />
            </div>
            <h3 className="font-semibold text-foreground">AI Insights</h3>
            <p className="text-sm text-muted-foreground">
              Our AI analyzes your choices with playful commentary
            </p>
          </div>
          <div className="space-y-3">
            <div className="p-3 rounded-lg bg-ai-accent/10 mx-auto w-fit">
              <Sparkles className="w-6 h-6 text-ai-accent" />
            </div>
            <h3 className="font-semibold text-foreground">Perfect Match</h3>
            <p className="text-sm text-muted-foreground">
              Discover your unique ice cream personality flavor
            </p>
          </div>
        </div>

        {/* Start Button */}
        <div className="pt-8">
          <Button 
            onClick={onStartGame}
            size="lg"
            className="text-lg px-12 py-6 bg-gradient-ai hover:shadow-ai-glow transition-all duration-300 animate-pulse-glow"
          >
            <IceCream className="w-6 h-6 mr-3" />
            Start Game
          </Button>
        </div>
      </div>
    </div>
  );
};