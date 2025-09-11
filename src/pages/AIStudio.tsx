import { useState, useEffect } from "react";
import { WelcomeScreen } from "@/components/WelcomeScreen";
import { PlayerSetup } from "@/components/PlayerSetup";
import { ImageSelectionRound, Round, ImageChoice } from "@/components/ImageSelectionRound";
import { AIThinkingScreen, ThinkingConversation } from "@/components/AIThinkingScreen";
import { aiConversationGenerator } from "@/utils/aiConversationGenerator";
import { FinalReveal, IceCreamPersonality } from "@/components/FinalReveal";
import { useIngredientsInventory } from "@/hooks/useIngredientsInventory";
import { toast } from "sonner";
import { apiService } from "@/services/api";

// Import images
import adventureAction from "@/assets/adventure-action.webp";
import classicRetro from "@/assets/classic-retro.webp";
import lightFruit from "@/assets/light-fruit.webp";
import richChocolate from "@/assets/rich-chocolate.jpg";
import smoothCream from "@/assets/smooth-cream.webp";
import crunchyNuts from "@/assets/crunchy-nuts.jpeg";
import rainbowSprinkles from "@/assets/rainbow-sprinkles.jpg";
import caramelDrizzle from "@/assets/caramel-drizzle.webp";

interface AIInteraction {
  selection: string;
  aiThought: string;
  aiEmoji: string;
  aiSteps: string[];
  round: number;
  timestamp: Date;
  enhanced_ai_response?: {
    reasoning_steps: string[];
    ingredient_mappings: Array<{
      ingredient: string;
      quantity: number;
      unit_cost: number;
      total_cost: number;
      category: string;
    }>;
    similar_flavors: string[];
    probable_ice_cream: string;
    cost_breakdown: {
      base_cost: number;
      ingredient_costs: number;
      preparation_cost: number;
      total_cost: number;
    };
    confidence_score: number;
  };
}

interface Player {
  id: string;
  name: string;
  selections: string[];
  totalCost: number;
  aiInteractions: AIInteraction[];
  generatedImageUrl?: string;
}

type GameState = 'setup' | 'welcome' | 'playing' | 'thinking' | 'reveal';

const AIStudio = () => {
  const [gameState, setGameState] = useState<GameState>('setup');
  const [players, setPlayers] = useState<Player[]>([]);
  const [currentPlayerIndex, setCurrentPlayerIndex] = useState(0);
  const [currentRoundIndex, setCurrentRoundIndex] = useState(0);
  const [currentThinking, setCurrentThinking] = useState<ThinkingConversation | null>(null);
  
  // Generate a unique session ID for this game session
  const [gameSessionId] = useState(() => `game-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`);
  
  // Use the new ingredients inventory hook
  const { 
    inventory, 
    isLoading: inventoryLoading, 
    error: inventoryError,
    resetInventory 
  } = useIngredientsInventory(Math.max(players.length, 4));

  const currentPlayer = players[currentPlayerIndex];

  // Show loading state while inventory is loading
  if (inventoryLoading) {
    return (
      <div className="min-h-screen bg-gradient-canvas flex items-center justify-center">
        <div className="text-center space-y-4">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-ai-primary mx-auto"></div>
          <p className="text-foreground">Loading ingredients...</p>
        </div>
      </div>
    );
  }

  // Show error state if inventory failed to load
  if (inventoryError) {
    return (
      <div className="min-h-screen bg-gradient-canvas flex items-center justify-center">
        <div className="text-center space-y-4">
          <p className="text-red-500">Failed to load ingredients: {inventoryError}</p>
          <button 
            onClick={() => window.location.reload()} 
            className="px-4 py-2 bg-ai-primary text-white rounded-lg hover:opacity-90"
          >
            Retry
          </button>
        </div>
      </div>
    );
  }

  const rounds: Round[] = [
    {
      id: 'style',
      category: '',
      question: 'What feels right to you?',
      choices: [
        {
          id: 'adventure',
          image: adventureAction,
          title: '',
          description: '',
          value: 'Adventure'
        },
        {
          id: 'classic',
          image: classicRetro,
          title: '',
          description: '',
          value: 'Classic'
        }
      ]
    },
    {
      id: 'sweetness',
      category: '',
      question: 'What feels right to you?',
      choices: [
        {
          id: 'light',
          image: lightFruit,
          title: '',
          description: '',
          value: 'Light'
        },
        {
          id: 'rich',
          image: richChocolate,
          title: '',
          description: '',
          value: 'Rich'
        }
      ]
    },
    {
      id: 'texture',
      category: '',
      question: 'What feels right to you?',
      choices: [
        {
          id: 'smooth',
          image: smoothCream,
          title: '',
          description: '',
          value: 'Smooth'
        },
        {
          id: 'crunchy',
          image: crunchyNuts,
          title: '',
          description: '',
          value: 'Crunchy'
        }
      ]
    },
    {
      id: 'toppings',
      category: '',
      question: 'What feels right to you?',
      choices: [
        {
          id: 'sprinkles',
          image: rainbowSprinkles,
          title: '',
          description: '',
          value: 'Sprinkles'
        },
        {
          id: 'caramel',
          image: caramelDrizzle,
          title: '',
          description: '',
          value: 'Caramel'
        }
      ]
    }
  ];


  const generatePersonality = (playerSelections: string[]): IceCreamPersonality => {
    // Check if everything was skipped (easter egg)
    const allSkipped = playerSelections.every(s => s === 'Skip');
    if (allSkipped) {
      return {
        name: "Empty Ice Cream Cone 🍦💨",
        emoji: "🙈💔",
        description: "Looks like you're as empty as this empty ice cream cone! You skipped everything! Maybe you're just too mysterious for our AI to figure out, or perhaps you're saving all your decisions for something really important. Either way, you've mastered the art of beautiful nothingness!",
        color: "#95a5a6",
        gradient: "linear-gradient(135deg, #bdc3c7, #2c3e50)",
        insights: [
          "You're a master of avoidance! 🦘",
          "Decision paralysis or pure genius? We may never know! 🤷‍♂️",
          "You keep everyone guessing with your mysterious ways! 🕵️‍♂️",
          "Maybe you're just too cool for regular ice cream choices! 😎"
        ]
      };
    }

    // Check for mostly skipped (more than half)
    const skipCount = playerSelections.filter(s => s === 'Skip').length;
    if (skipCount > playerSelections.length / 2) {
      return {
        name: "The Mysterious Skipper 🎭🦘",
        emoji: "🤷‍♂️✨",
        description: "You're beautifully unpredictable! With all that skipping, you keep everyone guessing. You march to the beat of your own drum and refuse to be put in a box. Decision avoidance is your superpower!",
        color: "#9b59b6",
        gradient: "linear-gradient(135deg, #9b59b6, #8e44ad)",
        insights: [
          "You're wonderfully unpredictable! 🎲",
          "Master of keeping people on their toes! 💃",
          "Your indecision is a form of art! 🎨",
          "Rules are more like... guidelines to you! 🏴‍☠️"
        ]
      };
    }

    // Filter out skips for regular personality generation
    const validSelections = playerSelections.filter(s => s !== 'Skip');
    
    // If we have some selections but not enough for full personality, generate a random one
    if (validSelections.length > 0 && validSelections.length < 4) {
      const availableFlavors = ['Adventure', 'Classic', 'Light', 'Rich', 'Smooth', 'Crunchy', 'Sprinkles', 'Caramel'];
      
      // Fill missing selections with random flavors, but favor the ones they did pick
      const filledSelections = [...validSelections];
      while (filledSelections.length < 4) {
        const randomFlavor = availableFlavors[Math.floor(Math.random() * availableFlavors.length)];
        filledSelections.push(randomFlavor);
      }
      
      // Use the filled selections but note it in the description
      const style = filledSelections[0];
      const sweetness = filledSelections[1];
      const texture = filledSelections[2];
      const topping = filledSelections[3];
      
      return generateCombinationPersonality(style, sweetness, texture, topping, true, skipCount);
    }

    // If no valid selections, return pure mystery
    if (validSelections.length === 0) {
      return {
        name: "Pure Mystery 🕵️‍♂️🔮",
        emoji: "❓💫",
        description: "You're an enigma wrapped in a riddle! We literally have no data on you!",
        color: "#34495e",
        gradient: "linear-gradient(135deg, #2c3e50, #34495e)",
        insights: ["You're completely unknowable! And that's fascinating! 🌌"]
      };
    }

    // Continue with regular personality generation using valid selections
    const style = validSelections[0];
    const sweetness = validSelections[1];
    const texture = validSelections[2];
    const topping = validSelections[3];

    return generateCombinationPersonality(style, sweetness, texture, topping, false, skipCount);
  };

  // Helper function to generate personality from combinations
  const generateCombinationPersonality = (
    style: string, 
    sweetness: string, 
    texture: string, 
    topping: string, 
    isPartiallyRandom: boolean, 
    skipCount: number
  ): IceCreamPersonality => {

    const combinations = {
      "Adventure-Rich-Crunchy-Sprinkles": {
        name: "Rainbow Hero Crunch 🌈💥",
        emoji: "🦸‍♂️🍦",
        description: "Bold adventurer with a sweet, colorful soul",
        color: "#ff6b6b",
        gradient: "linear-gradient(135deg, #ff6b6b, #4ecdc4)"
      },
      "Adventure-Rich-Crunchy-Caramel": {
        name: "Caramel Warrior Blast 🍯⚡",
        emoji: "⚔️🍦",
        description: "Fierce adventurer with refined taste",
        color: "#f39c12",
        gradient: "linear-gradient(135deg, #f39c12, #e74c3c)"
      },
      "Classic-Light-Smooth-Sprinkles": {
        name: "Classic Rainbow Dream 🍓✨",
        emoji: "👑🍦",
        description: "Elegant soul with a playful heart",
        color: "#e91e63",
        gradient: "linear-gradient(135deg, #e91e63, #9c27b0)"
      },
      "Classic-Light-Smooth-Caramel": {
        name: "Golden Elegance Swirl 🌟🍯",
        emoji: "👸🍦",
        description: "Timeless beauty with sophisticated taste",
        color: "#ffd700",
        gradient: "linear-gradient(135deg, #ffd700, #ff8f00)"
      }
    };

    const key = `${style}-${sweetness}-${texture}-${topping}`;
    const personality = combinations[key as keyof typeof combinations] || combinations["Classic-Light-Smooth-Caramel"];

    let finalDescription = personality.description;
    if (isPartiallyRandom && skipCount > 0) {
      finalDescription += ` With ${skipCount} skip${skipCount > 1 ? 's' : ''}, you added some mystery to your flavor journey!`;
    }

    return {
      ...personality,
      description: finalDescription,
      insights: [
        `${style} + ${sweetness} + ${texture} tells me you're someone who ${
          style === 'Adventure' ? 'loves bold experiences' : 'appreciates timeless beauty'
        }.`,
        `Your ${sweetness.toLowerCase()} preference shows you ${
          sweetness === 'Rich' ? 'embrace intensity and depth' : 'value balance and freshness'
        }.`,
        `The ${texture.toLowerCase()} texture choice reveals you ${
          texture === 'Smooth' ? 'appreciate refinement and elegance' : 'enjoy surprises and complexity'
        }.`,
        `And ${topping.toLowerCase()} on top? That's pure ${
          topping === 'Sprinkles' ? 'joy and playfulness' : 'sophistication and warmth'
        }!`,
        ...(isPartiallyRandom ? [`Your ${skipCount} skip${skipCount > 1 ? 's' : ''} added an element of beautiful unpredictability! 🎲`] : [])
      ]
    };
  };

  const handlePlayersReady = (newPlayers: Player[]) => {
    // Ensure all players have aiInteractions array
    const playersWithInteractions = newPlayers.map(player => ({
      ...player,
      aiInteractions: player.aiInteractions || []
    }));
    setPlayers(playersWithInteractions);
    setGameState('welcome');
    setCurrentPlayerIndex(0);
    setCurrentRoundIndex(0);
  };

  const handleStartGame = () => {
    setGameState('playing');
    setCurrentRoundIndex(0);
    setCurrentPlayerIndex(0);
  };

  const isAvailable = (choice: ImageChoice): boolean => {
    const ingredient = inventory[choice.value];
    return ingredient && ingredient.available > 0;
  };

  const handleSkip = () => {
    // Generate AI conversation for skip
    const conversation = aiConversationGenerator.generateConversation({
      currentSelection: 'Skip',
      previousSelections: currentPlayer.selections,
      roundNumber: currentRoundIndex + 1,
      playerName: currentPlayer.name,
      isSkipped: true
    });

    // Create AI interaction from conversation
    const aiInteraction: AIInteraction = {
      selection: 'Skip',
      aiThought: conversation.finalResponse.text,
      aiEmoji: conversation.finalResponse.emoji,
      aiSteps: conversation.steps.map(step => step.text),
      round: currentRoundIndex + 1,
      timestamp: new Date()
    };
    
    const updatedPlayer = {
      ...currentPlayer,
      selections: [...currentPlayer.selections, 'Skip'],
      aiInteractions: [...currentPlayer.aiInteractions, aiInteraction]
    };

    const newPlayers = [...players];
    newPlayers[currentPlayerIndex] = updatedPlayer;
    setPlayers(newPlayers);
    
    setCurrentThinking(conversation);
    setGameState('thinking');
  };

  const handleSelection = (choice: ImageChoice) => {
    if (!currentPlayer || !isAvailable(choice)) {
      toast.error("This ingredient is out of stock!");
      return;
    }

    // Generate AI conversation
    const conversation = aiConversationGenerator.generateConversation({
      currentSelection: choice.value,
      previousSelections: currentPlayer.selections,
      roundNumber: currentRoundIndex + 1,
      playerName: currentPlayer.name
    });

    // Create AI interaction
    const aiInteraction: AIInteraction = {
      selection: choice.value,
      aiThought: conversation.finalResponse.text,
      aiEmoji: conversation.finalResponse.emoji,
      aiSteps: conversation.steps.map(step => step.text),
      round: currentRoundIndex + 1,
      timestamp: new Date()
    };

    // Update player
    const updatedPlayer = {
      ...currentPlayer,
      selections: [...currentPlayer.selections, choice.value],
      totalCost: currentPlayer.totalCost + inventory[choice.value].price,
      aiInteractions: [...currentPlayer.aiInteractions, aiInteraction]
    };

    // Note: Inventory updates removed as per Phase 8 - backend handles inventory during processing

    // Update players array
    const updatedPlayers = players.map(p => 
      p.id === currentPlayer.id ? updatedPlayer : p
    );

    setPlayers(updatedPlayers);
    setCurrentThinking(conversation);
    setGameState('thinking');

    // Save to localStorage
    localStorage.setItem('iceCreamGamePlayers', JSON.stringify(updatedPlayers));
  };

  const handleThinkingComplete = (processingResult?: any) => {
    // Handle processing result from backend
    if (processingResult) {
      setPlayers(prev => prev.map(player => {
        if (player.id === currentPlayer.id) {
          // Update the player with backend processing results
          const updatedPlayer = { 
            ...player, 
            totalCost: processingResult.estimatedCost || player.totalCost,
            generatedImageUrl: processingResult.imageUrl // Store the generated image URL
          };

          // If we have enhanced AI response, update the latest AI interaction
          if (processingResult.processedResults?.enhanced_ai_response && player.aiInteractions.length > 0) {
            const updatedInteractions = [...player.aiInteractions];
            const lastInteractionIndex = updatedInteractions.length - 1;
            updatedInteractions[lastInteractionIndex] = {
              ...updatedInteractions[lastInteractionIndex],
              enhanced_ai_response: processingResult.processedResults.enhanced_ai_response
            };
            updatedPlayer.aiInteractions = updatedInteractions;
          }

          return updatedPlayer;
        }
        return player;
      }));
      
      console.log("✅ Updated player with backend data:", {
        cost: processingResult.estimatedCost,
        imageUrl: processingResult.imageUrl,
        hasEnhancedResponse: !!processingResult.processedResults?.enhanced_ai_response
      });
    }
    
    if (processingResult?.error) {
      console.warn("⚠️ Processing completed with error:", processingResult.error);
      toast.error("AI processing had issues, but continuing with game");
    }
    
    if (currentRoundIndex < rounds.length - 1) {
      setCurrentRoundIndex(prev => prev + 1);
      setGameState('playing');
    } else {
      // Move to next player or finish game
      if (currentPlayerIndex < players.length - 1) {
        setCurrentPlayerIndex(prev => prev + 1);
        setCurrentRoundIndex(0);
        setGameState('playing');
        toast.success(`${players[currentPlayerIndex + 1].name}'s turn!`);
      } else {
        setGameState('reveal');
      }
    }
  };

  const handlePlayAgain = () => {
    // Reset game but preserve inventory for persistent ingredient usage
    localStorage.removeItem('iceCreamGamePlayers');
    setGameState('setup');
    setPlayers([]);
    setCurrentPlayerIndex(0);
    setCurrentRoundIndex(0);
    setCurrentThinking(null);
    
    // Keep the current inventory state - don't reset it
  };

  const handleShare = () => {
    const shareText = `Check out our ice cream personalities! 🍦 Play the game and discover yours too!`;
    
    if (navigator.share) {
      navigator.share({
        title: 'Ice Cream Personality Game',
        text: shareText,
        url: window.location.href
      }).catch(() => {
        navigator.clipboard.writeText(`${shareText} ${window.location.href}`);
        toast.success("Share text copied to clipboard!");
      });
    } else {
      navigator.clipboard.writeText(`${shareText} ${window.location.href}`);
      toast.success("Share text copied to clipboard!");
    }
  };

  if (gameState === 'setup') {
    return <PlayerSetup onPlayersReady={handlePlayersReady} />;
  }

  if (gameState === 'welcome') {
    return <WelcomeScreen onStartGame={handleStartGame} />;
  }

  if (gameState === 'playing' && currentPlayer) {
    return (
      <ImageSelectionRound
        round={rounds[currentRoundIndex]}
        onSelect={handleSelection}
        onSkip={handleSkip}
        currentRound={currentRoundIndex + 1}
        totalRounds={rounds.length}
        player={currentPlayer}
        inventory={inventory}
      />
    );
  }

  if (gameState === 'thinking' && currentThinking && currentPlayer) {
    const playerData = {
      id: currentPlayer.id,
      name: currentPlayer.name,
      selections: currentPlayer.selections,
      personality: undefined // Will be generated by backend
    };
    
    return (
      <AIThinkingScreen
        playerData={playerData}
        conversation={currentThinking}
        onComplete={handleThinkingComplete}
        duration={6000}
      />
    );
  }

  if (gameState === 'reveal') {
    return (
      <FinalReveal
        players={players}
        generatePersonality={generatePersonality}
        onPlayAgain={handlePlayAgain}
        onShare={handleShare}
        gameSessionId={gameSessionId}
      />
    );
  }

  return null;
};

export default AIStudio;