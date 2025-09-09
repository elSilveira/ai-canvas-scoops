import { useState } from "react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Card } from "@/components/ui/card";

interface Player {
  id: string;
  name: string;
  budget: number;
  selections: string[];
}

interface PlayerSetupProps {
  onPlayersReady: (players: Player[]) => void;
}

export const PlayerSetup = ({ onPlayersReady }: PlayerSetupProps) => {
  const [playerNames, setPlayerNames] = useState<string[]>(['']);
  const [isStarting, setIsStarting] = useState(false);

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
      budget: 100, // Each player starts with $100
      selections: []
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
        <div className="text-center space-y-4 animate-fade-in">
          <h1 className="text-4xl md:text-6xl font-bold bg-gradient-ai bg-clip-text text-transparent">
            Player Setup 👥
          </h1>
          <p className="text-lg text-muted-foreground">
            Enter player names. Each player gets $100 to spend on ingredients!
          </p>
        </div>

        <Card className="p-8 space-y-6 bg-surface-elevated border-surface-border animate-fade-in">
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
              className="px-8 py-6 text-lg font-semibold"
              size="lg"
            >
              {isStarting ? "Starting Game..." : `Start Game with ${validPlayerCount} Player${validPlayerCount !== 1 ? 's' : ''}`}
            </Button>
          </div>
        </Card>
      </div>
    </div>
  );
};