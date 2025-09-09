import { useState } from "react";
import { WelcomeScreen } from "@/components/WelcomeScreen";
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

type GameState = 'welcome' | 'playing' | 'thinking' | 'reveal';

const AIStudio = () => {
  const [gameState, setGameState] = useState<GameState>('welcome');
  const [currentRoundIndex, setCurrentRoundIndex] = useState(0);
  const [selections, setSelections] = useState<string[]>([]);
  const [currentThinking, setCurrentThinking] = useState<ThinkingComment | null>(null);

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

  const generatePersonality = (): IceCreamPersonality => {
    const style = selections[0];
    const sweetness = selections[1];
    const texture = selections[2];
    const topping = selections[3];

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

  const handleStartGame = () => {
    setGameState('playing');
    setCurrentRoundIndex(0);
    setSelections([]);
  };

  const handleSelection = (choice: ImageChoice) => {
    const newSelections = [...selections, choice.value];
    setSelections(newSelections);
    setCurrentThinking(thinkingComments[choice.value]);
    setGameState('thinking');
  };

  const handleThinkingComplete = () => {
    if (currentRoundIndex < rounds.length - 1) {
      setCurrentRoundIndex(prev => prev + 1);
      setGameState('playing');
    } else {
      setGameState('reveal');
    }
  };

  const handlePlayAgain = () => {
    setGameState('welcome');
    setCurrentRoundIndex(0);
    setSelections([]);
    setCurrentThinking(null);
  };

  const handleShare = () => {
    const personality = generatePersonality();
    const shareText = `I just discovered I'm a ${personality.name}! 🍦 Find out your ice cream personality too!`;
    
    if (navigator.share) {
      navigator.share({
        title: 'My Ice Cream Personality',
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

  if (gameState === 'welcome') {
    return <WelcomeScreen onStartGame={handleStartGame} />;
  }

  if (gameState === 'playing') {
    return (
      <ImageSelectionRound
        round={rounds[currentRoundIndex]}
        onSelect={handleSelection}
        currentRound={currentRoundIndex + 1}
        totalRounds={rounds.length}
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
        personality={generatePersonality()}
        selections={selections}
        onPlayAgain={handlePlayAgain}
        onShare={handleShare}
      />
    );
  }

  return null;
};

export default AIStudio;