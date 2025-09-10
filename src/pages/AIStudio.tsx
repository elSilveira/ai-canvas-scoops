import { useState, useEffect } from "react";
import { WelcomeScreen } from "@/components/WelcomeScreen";
import { PlayerSetup } from "@/components/PlayerSetup";
import { ImageSelectionRound, Round, ImageChoice } from "@/components/ImageSelectionRound";
import { AIThinkingScreen, ThinkingComment } from "@/components/AIThinkingScreen";
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
  const [currentThinking, setCurrentThinking] = useState<ThinkingComment | null>(null);

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

  const thinkingComments: { [key: string]: ThinkingComment } = {
    Adventure: { text: "Hmm… action hero, huh? Bold choice! 🚀", emoji: "💥" },
    Classic: { text: "A timeless soul! I sense elegance... ✨", emoji: "🎭" },
    Light: { text: "Fresh and bright - you love balance! 🌟", emoji: "🍃" },
    Rich: { text: "I see you like it rich… interesting 🍫", emoji: "🍫" },
    Smooth: { text: "Smooth operator! You appreciate finesse 😌", emoji: "✨" },
    Crunchy: { text: "Texture lover! You like surprises 🎉", emoji: "🥜" },
    Sprinkles: { text: "Playful spirit detected! Life's a party 🎊", emoji: "🌈" },
    Caramel: { text: "Sweet sophistication - you know quality! 👌", emoji: "🍯" }
  };

  const generatePersonality = (playerSelections: string[]): IceCreamPersonality => {
    const style = playerSelections[0];
    const sweetness = playerSelections[1];
    const texture = playerSelections[2];
    const topping = playerSelections[3];

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

  const handleSelection = (choice: ImageChoice) => {
    if (!currentPlayer || !isAvailable(choice)) {
      toast.error("This ingredient is out of stock!");
      return;
    }

    // Create AI interaction
    const aiInteraction: AIInteraction = {
      selection: choice.value,
      aiThought: thinkingComments[choice.value].text,
      aiEmoji: thinkingComments[choice.value].emoji,
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
    setCurrentThinking(thinkingComments[choice.value]);
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
        comment={currentThinking}
        onComplete={handleThinkingComplete}
        duration={3000}
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