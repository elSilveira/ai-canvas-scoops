import { useState, useEffect } from "react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Card } from "@/components/ui/card";
import { Alert, AlertDescription } from "@/components/ui/alert";
import { CheckCircle, AlertTriangle, Loader2 } from "lucide-react";
import * as api from "@/services/api";

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
  generatedImageUrl?: string;
}

interface PlayerSetupProps {
  onPlayersReady: (players: Player[]) => void;
}

export const PlayerSetup = ({ onPlayersReady }: PlayerSetupProps) => {
  const [playerNames, setPlayerNames] = useState<string[]>(['']);
  const [isStarting, setIsStarting] = useState(false);
  const [systemStatus, setSystemStatus] = useState<'checking' | 'ready' | 'error'>('checking');
  const [statusMessage, setStatusMessage] = useState('');

  // Check backend health on component mount
  useEffect(() => {
    const checkSystemHealth = async () => {
      try {
        const health = await api.checkHealth();
        console.log('🔍 Backend health check:', health);
        
        // Also check if we can get ingredients
        const mappings = await api.getSelectionMappings();
        console.log('🔍 Selection mappings available:', mappings.length);
        
        setSystemStatus('ready');
        setStatusMessage(`🟢 AI Canvas ready! ${mappings.length} ingredients loaded`);
      } catch (error) {
        console.error('❌ System health check failed:', error);
        setSystemStatus('error');
        setStatusMessage('⚠️ Backend not available - using demo mode');
      }
    };

    checkSystemHealth();
  }, []);

  const addPlayer = () => {
    if (playerNames.length < 4) {
      setPlayerNames([...playerNames, '']);
    }
  };

  const removePlayer = (index: number) => {
    if (playerNames.length > 1) {
      setPlayerNames(playerNames.filter((_, i) => i !== index));
    }
  };

  const updatePlayerName = (index: number, name: string) => {
    const newNames = [...playerNames];
    newNames[index] = name;
    setPlayerNames(newNames);
  };

  const startGame = () => {
    const validNames = playerNames.filter(name => name.trim() !== '');
    if (validNames.length === 0) return;

    setIsStarting(true);
    const players: Player[] = validNames.map((name, index) => ({
      id: `player_${index + 1}`,
      name: name.trim(),
      selections: [],
      totalCost: 0,
      aiInteractions: []
    }));

    // Save to localStorage
    localStorage.setItem('iceCreamGamePlayers', JSON.stringify(players));
    
    setTimeout(() => {
      onPlayersReady(players);
    }, 1000);
  };

  const validPlayerCount = playerNames.filter(name => name.trim() !== '').length;

  return (
    <div className="min-h-screen bg-gradient-canvas p-6 flex items-center justify-center">
      <div className="max-w-2xl mx-auto w-full space-y-8">
        {/* STAMPalooza Header */}
        <div className="text-center space-y-6 animate-fade-in">
          <div className="flex items-center justify-center">
            <img 
              src="/lovable-uploads/44b187ad-1d73-4392-a7fb-0674a8c45a95.png" 
              alt="STAMPalooza Logo" 
              className="w-48 h-48 md:w-64 md:h-64 lg:w-80 lg:h-80"
            />
          </div>
          <p className="text-lg text-muted-foreground">
            Enter player names to start the ice cream personality game!
          </p>
        </div>

        <Card className="p-8 space-y-6 bg-surface-elevated border-surface-border animate-fade-in">
          {/* System Status */}
          <Alert className={`${systemStatus === 'ready' ? 'border-green-500/50 bg-green-500/10' : 
                            systemStatus === 'error' ? 'border-yellow-500/50 bg-yellow-500/10' : 
                            'border-blue-500/50 bg-blue-500/10'}`}>
            <div className="flex items-center gap-2">
              {systemStatus === 'checking' && <Loader2 className="w-4 h-4 animate-spin" />}
              {systemStatus === 'ready' && <CheckCircle className="w-4 h-4 text-green-500" />}
              {systemStatus === 'error' && <AlertTriangle className="w-4 h-4 text-yellow-500" />}
              <AlertDescription>{statusMessage}</AlertDescription>
            </div>
          </Alert>

          <div className="space-y-4">
            {playerNames.map((name, index) => (
              <div key={index} className="flex gap-3 items-center">
                <div className="flex-1">
                  <Input
                    placeholder={`Player ${index + 1} name`}
                    value={name}
                    onChange={(e) => updatePlayerName(index, e.target.value)}
                    className="text-lg"
                  />
                </div>
                {playerNames.length > 1 && (
                  <Button
                    variant="ghost"
                    size="sm"
                    onClick={() => removePlayer(index)}
                    className="text-destructive hover:text-destructive"
                  >
                    Remove
                  </Button>
                )}
              </div>
            ))}
          </div>

          <div className="flex gap-3">
            {playerNames.length < 4 && (
              <Button
                variant="outline"
                onClick={addPlayer}
                className="flex-1"
              >
                Add Player (+)
              </Button>
            )}
          </div>

          <div className="text-center space-y-4">
            <p className="text-sm text-muted-foreground">
              {validPlayerCount} player{validPlayerCount !== 1 ? 's' : ''} ready
            </p>
            <Button
              onClick={startGame}
              disabled={validPlayerCount === 0 || isStarting}
              className="px-8 py-6 text-lg font-semibold bg-gradient-ai hover:shadow-festive"
              size="lg"
            >
              {isStarting ? "Starting Game..." : `🍦 Begin STAMPalooza with ${validPlayerCount} Player${validPlayerCount !== 1 ? 's' : ''}`}
            </Button>
          </div>
        </Card>
      </div>
    </div>
  );
};