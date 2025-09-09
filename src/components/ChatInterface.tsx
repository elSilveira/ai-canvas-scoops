import { useState, useRef, useEffect } from "react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Send, Sparkles, Brain } from "lucide-react";
import { cn } from "@/lib/utils";

interface Message {
  id: string;
  type: 'user' | 'ai-thought' | 'ai-response';
  content: string;
  timestamp: Date;
}

interface ChatInterfaceProps {
  onGenerate: (prompt: string) => void;
  isGenerating: boolean;
}

export const ChatInterface = ({ onGenerate, isGenerating }: ChatInterfaceProps) => {
  const [messages, setMessages] = useState<Message[]>([
    {
      id: '1',
      type: 'ai-response',
      content: "Hi! I'm your AI creative assistant. Describe what you'd like me to create and I'll generate it for you!",
      timestamp: new Date(),
    }
  ]);
  const [inputValue, setInputValue] = useState("");
  const [isThinking, setIsThinking] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!inputValue.trim() || isGenerating) return;

    const userMessage: Message = {
      id: Date.now().toString(),
      type: 'user',
      content: inputValue.trim(),
      timestamp: new Date(),
    };

    setMessages(prev => [...prev, userMessage]);
    const prompt = inputValue.trim();
    setInputValue("");
    setIsThinking(true);

    // Simulate AI thinking process
    setTimeout(() => {
      const thoughtMessage: Message = {
        id: (Date.now() + 1).toString(),
        type: 'ai-thought',
        content: "Let me analyze your request and create something amazing...",
        timestamp: new Date(),
      };
      setMessages(prev => [...prev, thoughtMessage]);
      
      setTimeout(() => {
        const responseMessage: Message = {
          id: (Date.now() + 2).toString(),
          type: 'ai-response',
          content: "Perfect! I'm generating your creation now. Watch the canvas!",
          timestamp: new Date(),
        };
        setMessages(prev => [...prev, responseMessage]);
        setIsThinking(false);
        onGenerate(prompt);
      }, 1500);
    }, 800);
  };

  const formatTime = (timestamp: Date) => {
    return timestamp.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
  };

  return (
    <div className="flex flex-col h-full bg-gradient-chat rounded-xl border border-border/50">
      {/* Chat Header */}
      <div className="p-6 border-b border-border/50">
        <div className="flex items-center gap-3">
          <div className="p-2 rounded-lg bg-gradient-ai">
            <Sparkles className="w-5 h-5 text-white" />
          </div>
          <div>
            <h2 className="text-xl font-semibold text-foreground">AI Creative Assistant</h2>
            <p className="text-sm text-muted-foreground">Describe what you want to create</p>
          </div>
        </div>
      </div>

      {/* Messages */}
      <div className="flex-1 overflow-y-auto p-6 space-y-4">
        {messages.map((message) => (
          <div
            key={message.id}
            className={cn(
              "flex items-start gap-3 animate-fade-in",
              message.type === 'user' ? "flex-row-reverse" : "flex-row"
            )}
          >
            {message.type !== 'user' && (
              <div className={cn(
                "flex-shrink-0 w-8 h-8 rounded-full flex items-center justify-center",
                message.type === 'ai-thought' ? "bg-ai-secondary/20" : "bg-gradient-ai"
              )}>
                {message.type === 'ai-thought' ? (
                  <Brain className="w-4 h-4 text-ai-secondary" />
                ) : (
                  <Sparkles className="w-4 h-4 text-white" />
                )}
              </div>
            )}
            
            <div
              className={cn(
                "max-w-[80%] rounded-2xl px-4 py-3 transition-all duration-300",
                message.type === 'user'
                  ? "bg-primary text-primary-foreground ml-auto"
                  : message.type === 'ai-thought'
                  ? "bg-ai-secondary/10 border border-ai-secondary/20 text-foreground"
                  : "bg-surface-elevated text-foreground"
              )}
            >
              <p className="text-sm leading-relaxed">{message.content}</p>
              <span className="text-xs opacity-70 mt-1 block">
                {formatTime(message.timestamp)}
              </span>
            </div>

            {message.type === 'user' && (
              <div className="flex-shrink-0 w-8 h-8 rounded-full bg-primary flex items-center justify-center">
                <span className="text-xs font-medium text-primary-foreground">You</span>
              </div>
            )}
          </div>
        ))}
        
        {isThinking && (
          <div className="flex items-start gap-3 animate-fade-in">
            <div className="flex-shrink-0 w-8 h-8 rounded-full bg-ai-secondary/20 flex items-center justify-center">
              <Brain className="w-4 h-4 text-ai-secondary animate-pulse" />
            </div>
            <div className="bg-ai-secondary/10 border border-ai-secondary/20 rounded-2xl px-4 py-3">
              <div className="flex items-center gap-2">
                <div className="flex gap-1">
                  <div className="w-2 h-2 bg-ai-secondary/60 rounded-full animate-typing"></div>
                  <div className="w-2 h-2 bg-ai-secondary/60 rounded-full animate-typing" style={{ animationDelay: '0.2s' }}></div>
                  <div className="w-2 h-2 bg-ai-secondary/60 rounded-full animate-typing" style={{ animationDelay: '0.4s' }}></div>
                </div>
                <span className="text-xs text-muted-foreground">AI is thinking...</span>
              </div>
            </div>
          </div>
        )}
        <div ref={messagesEndRef} />
      </div>

      {/* Input */}
      <div className="p-6 border-t border-border/50">
        <form onSubmit={handleSubmit} className="flex gap-3">
          <Input
            value={inputValue}
            onChange={(e) => setInputValue(e.target.value)}
            placeholder="Describe what you want to create..."
            className="bg-surface border-border/50 focus:border-primary transition-colors"
            disabled={isGenerating}
          />
          <Button 
            type="submit" 
            size="icon"
            className="bg-gradient-ai hover:shadow-ai transition-all duration-300 disabled:opacity-50"
            disabled={!inputValue.trim() || isGenerating}
          >
            <Send className="w-4 h-4" />
          </Button>
        </form>
      </div>
    </div>
  );
};