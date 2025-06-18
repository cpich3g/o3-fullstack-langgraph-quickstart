import { useState } from "react";
import { Button } from "@/components/ui/button";
import { Textarea } from "@/components/ui/textarea";
import { Card, CardContent } from "@/components/ui/card";
import { 
  Zap,
  Send,
  X,
  Plus
} from "lucide-react";
import { cn } from "@/lib/utils";

interface AdvancedInputFormProps {
  onSubmit: (inputValue: string, effort: string) => void;
  isLoading: boolean;
  onCancel: () => void;
  hasHistory?: boolean;
  textareaRef?: React.RefObject<HTMLTextAreaElement | null>;
}

export function AdvancedInputForm({
  onSubmit,
  isLoading,
  onCancel,
  hasHistory = false,
  textareaRef
}: AdvancedInputFormProps) {
  const [inputValue, setInputValue] = useState("");
  const [selectedEffort, setSelectedEffort] = useState("medium");

  const handleSubmit = () => {
    if (!inputValue.trim()) return;
    onSubmit(inputValue, selectedEffort);
    setInputValue("");
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSubmit();
    }
  };  const effortOptions = [
    { value: "low", label: "Quick", description: "1 query, 1 loop", color: "text-green-400" },
    { value: "medium", label: "Balanced", description: "3 queries, 3 loops", color: "text-blue-400" },
    { value: "high", label: "Thorough", description: "10 queries, 30 loops", color: "text-purple-400" }
  ];

  return (
    <div className="w-full max-w-4xl mx-auto p-4 space-y-4">
      {/* Main Input Area */}
      <Card className="bg-card/50 backdrop-blur-sm border-border/50 shadow-lg">
        <CardContent className="p-4">
          <div className="space-y-4">
            {/* Text Input */}
            <div className="relative">              <Textarea
                ref={textareaRef}
                value={inputValue}
                onChange={(e) => setInputValue(e.target.value)}
                onKeyDown={handleKeyPress}
                placeholder="What would you like to research? Be specific for better results..."
                className="min-h-[60px] max-h-32 resize-none border-border/40 bg-background/80 backdrop-blur-sm focus:border-blue-500/50 focus:ring-2 focus:ring-blue-500/20 transition-all duration-200"
                disabled={isLoading}
              />
              
              {/* Character count */}
              <div className="absolute bottom-2 right-2 text-xs text-muted-foreground">
                {inputValue.length}/500
              </div>
            </div>            {/* Quick Action Buttons */}
            <div className="flex items-center justify-between gap-3">
              <div className="flex items-center gap-2">
                {/* Effort Quick Select */}
                <div className="flex items-center gap-1">
                  {effortOptions.map((option) => (
                    <Button
                      key={option.value}
                      variant={selectedEffort === option.value ? "secondary" : "ghost"}
                      size="sm"
                      onClick={() => setSelectedEffort(option.value)}
                      className={cn(
                        "text-xs transition-all duration-200",
                        selectedEffort === option.value && option.color
                      )}
                    >
                      <Zap className="w-3 h-3 mr-1" />
                      {option.label}
                    </Button>
                  ))}
                </div>
              </div>{/* Action Buttons */}
              <div className="flex items-center gap-2">
                {hasHistory && (
                  <Button
                    variant="ghost"
                    size="sm"
                    onClick={() => window.location.reload()}
                    className="text-muted-foreground hover:text-foreground border-border/40"
                    title="Start New Session"
                  >
                    <Plus className="w-4 h-4 mr-2" />
                    New Session
                  </Button>
                )}

                {isLoading && (
                  <Button
                    variant="outline"
                    size="sm"
                    onClick={onCancel}
                    className="text-red-400 hover:text-red-300 border-red-500/40"
                  >
                    <X className="w-4 h-4 mr-2" />
                    Cancel
                  </Button>
                )}
                
                <Button
                  onClick={handleSubmit}
                  disabled={!inputValue.trim() || isLoading}
                  className="bg-gradient-to-r from-blue-500 to-indigo-500 hover:from-blue-600 hover:to-indigo-600 text-white border-0 shadow-lg hover:shadow-xl transition-all duration-200 disabled:opacity-50"
                >
                  <Send className="w-4 h-4 mr-2" />
                  {isLoading ? "Researching..." : "Research"}
                </Button>
              </div>
            </div>
          </div>
        </CardContent>      </Card>
    </div>
  );
}
