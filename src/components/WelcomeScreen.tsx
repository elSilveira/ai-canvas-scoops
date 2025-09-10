import { Button } from "@/components/ui/button";
import { Sparkles, IceCream } from "lucide-react";

interface WelcomeScreenProps {
  onStartGame: () => void;
}

export const WelcomeScreen = ({ onStartGame }: WelcomeScreenProps) => {
  return (
    <div className="flex items-center justify-center min-h-screen bg-gradient-canvas p-6">
      <div className="text-center max-w-3xl mx-auto space-y-10 animate-fade-in">
        
        {/* STAMPalooza Header */}
        <div className="space-y-6">
          <div className="flex items-center justify-center">
            <img 
              src="/lovable-uploads/44b187ad-1d73-4392-a7fb-0674a8c45a95.png" 
              alt="STAMPalooza - Festival of Flavors" 
              className="w-32 h-32 md:w-40 md:h-40"
            />
          </div>
        </div>

        {/* Game Description */}
        <div className="space-y-4">
          <h2 className="text-3xl md:text-4xl font-bold text-foreground">
            Which Ice Cream Flavor Are You?
          </h2>
          <p className="text-xl text-muted-foreground leading-relaxed max-w-2xl mx-auto">
            Pick the images that match your vibe — from action movies to sweet toppings — 
            and let our AI scoop out your perfect flavor personality!
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
            className="text-xl px-12 py-6 bg-gradient-ai hover:shadow-festive transition-all duration-300 animate-pulse-glow"
          >
            <IceCream className="w-6 h-6 mr-3" />
            Start Your Flavor Journey
          </Button>
        </div>
      </div>
    </div>
  );
};