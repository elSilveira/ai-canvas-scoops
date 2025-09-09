import { useState } from "react";
import { ChatInterface } from "@/components/ChatInterface";
import { VisualCanvas } from "@/components/VisualCanvas";

const AIStudio = () => {
  const [isGenerating, setIsGenerating] = useState(false);
  const [currentPrompt, setCurrentPrompt] = useState<string | null>(null);

  const handleGenerate = (prompt: string) => {
    setCurrentPrompt(prompt);
    setIsGenerating(true);
    
    // Simulate generation process
    setTimeout(() => {
      setIsGenerating(false);
    }, 3000);
  };

  return (
    <div className="min-h-screen bg-background p-4">
      <div className="container mx-auto h-screen max-h-screen">
        {/* Header */}
        <header className="mb-6 pt-4">
          <div className="text-center space-y-2">
            <h1 className="text-4xl font-bold bg-gradient-ai bg-clip-text text-transparent">
              AI Creative Studio
            </h1>
            <p className="text-muted-foreground max-w-2xl mx-auto">
              Chat with AI to create amazing visuals. Describe your ideas and watch them come to life!
            </p>
          </div>
        </header>

        {/* Main Content */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 h-[calc(100vh-8rem)]">
          {/* Chat Panel */}
          <div className="h-full">
            <ChatInterface 
              onGenerate={handleGenerate}
              isGenerating={isGenerating}
            />
          </div>

          {/* Canvas Panel */}
          <div className="h-full">
            <VisualCanvas 
              isGenerating={isGenerating}
              currentPrompt={currentPrompt}
            />
          </div>
        </div>
      </div>
    </div>
  );
};

export default AIStudio;