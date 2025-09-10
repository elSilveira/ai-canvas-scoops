import { useState, useEffect } from "react";
import { WelcomeScreen } from "@/components/WelcomeScreen";
import { PlayerSetup } from "@/components/PlayerSetup";
import { ImageSelectionRound, Round, ImageChoice } from "@/components/ImageSelectionRound";
import { AIThinkingScreen, ThinkingConversation } from "@/components/AIThinkingScreen";
import { aiConversationGenerator } from "@/utils/aiConversationGenerator";
import { FinalReveal, IceCreamPersonality } from "@/components/FinalReveal";
import { toast } from "sonner";

// Import images
import adventureAction from "@/assets/adventure-action.jpg";
import classicRetro from "@/assets/classic-retro.jpg";
import lightFruit from "@/assets/light-fruit.jpg";
import richChocolate from "@/assets/rich-chocolate.jpg";
import smoothCream from "@/assets/smooth-cream.jpg";
import crunchyNuts from "@/assets/crunchy-nuts.jpg";
import rainbowSprinkles from "@/assets/rainbow-sprinkles.jpg";
import caramelDrizzle from "@/assets/caramel-drizzle.jpg";

interface AIInteraction {
  selection: string;
  aiThought: string;
  aiEmoji: string;
  aiSteps: string[];
  round: number;
  timestamp: Date;
}

interface Player {
  id: string;
  name: string;
  selections: string[];
  totalCost: number;
  aiInteractions: AIInteraction[];
}

interface GameInventory {
  [key: string]: {
    available: number;
    price: number;
  };
}

type GameState = 'setup' | 'welcome' | 'playing' | 'thinking' | 'reveal';

const AIStudio = () => {
  const [gameState, setGameState] = useState<GameState>('setup');
  const [players, setPlayers] = useState<Player[]>([]);
  const [currentPlayerIndex, setCurrentPlayerIndex] = useState(0);
  const [currentRoundIndex, setCurrentRoundIndex] = useState(0);
  const [inventory, setInventory] = useState<GameInventory>({});
  const [currentThinking, setCurrentThinking] = useState<ThinkingConversation | null>(null);

  // Initialize inventory with prices and quantities based on number of players
  useEffect(() => {
    const maxPlayers = Math.max(players.length, 4); // Default to 4 if no players yet
    const initialInventory: GameInventory = {
      Adventure: { available: maxPlayers, price: 15 },
      Classic: { available: maxPlayers, price: 10 },
      Light: { available: maxPlayers, price: 12 },
      Rich: { available: maxPlayers, price: 15 },
      Smooth: { available: maxPlayers, price: 10 },
      Crunchy: { available: maxPlayers, price: 13 },
      Sprinkles: { available: maxPlayers, price: 14 },
      Caramel: { available: maxPlayers, price: 15 }
    };
    
    // Load from localStorage if exists
    const savedInventory = localStorage.getItem('iceCreamGameInventory');
    if (savedInventory) {
      setInventory(JSON.parse(savedInventory));
    } else {
      setInventory(initialInventory);
      localStorage.setItem('iceCreamGameInventory', JSON.stringify(initialInventory));
    }
  }, [players.length]);

  const currentPlayer = players[currentPlayerIndex];

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
    const style = validSelections[0] || 'Classic';
    const sweetness = validSelections[1] || 'Light';
    const texture = validSelections[2] || 'Smooth';
    const topping = validSelections[3] || 'Sprinkles';

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

    return {
      ...personality,
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
        }!`
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

    // Update inventory
    const updatedInventory = {
      ...inventory,
      [choice.value]: {
        ...inventory[choice.value],
        available: inventory[choice.value].available - 1
      }
    };

    // Update players array
    const updatedPlayers = players.map(p => 
      p.id === currentPlayer.id ? updatedPlayer : p
    );

    setPlayers(updatedPlayers);
    setInventory(updatedInventory);
    setCurrentThinking(conversation);
    setGameState('thinking');

    // Save to localStorage
    localStorage.setItem('iceCreamGamePlayers', JSON.stringify(updatedPlayers));
    localStorage.setItem('iceCreamGameInventory', JSON.stringify(updatedInventory));
  };

  const handleThinkingComplete = () => {
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
    // Reset game
    localStorage.removeItem('iceCreamGamePlayers');
    localStorage.removeItem('iceCreamGameInventory');
    setGameState('setup');
    setPlayers([]);
    setCurrentPlayerIndex(0);
    setCurrentRoundIndex(0);
    setCurrentThinking(null);
    
    // Reset inventory
    const maxPlayers = Math.max(players.length, 4);
    const initialInventory: GameInventory = {
      Adventure: { available: maxPlayers, price: 15 },
      Classic: { available: maxPlayers, price: 10 },
      Light: { available: maxPlayers, price: 12 },
      Rich: { available: maxPlayers, price: 15 },
      Smooth: { available: maxPlayers, price: 10 },
      Crunchy: { available: maxPlayers, price: 13 },
      Sprinkles: { available: maxPlayers, price: 14 },
      Caramel: { available: maxPlayers, price: 15 }
    };
    setInventory(initialInventory);
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

  if (gameState === 'thinking' && currentThinking) {
    return (
      <AIThinkingScreen
        conversation={currentThinking}
        onComplete={handleThinkingComplete}
        duration={4000}
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
      />
    );
  }

  return null;
};

export default AIStudio;