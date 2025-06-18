import { useState } from "react";
import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import { ScrollArea } from "@/components/ui/scroll-area";
import { 
  History, 
  ChevronLeft,
  MessageSquare,
  Search,
  Trash2,
  Clock
} from "lucide-react";
import { cn } from "@/lib/utils";

interface ChatSession {
  id: string;
  title: string;
  timestamp: Date;
  messageCount: number;
  lastMessage: string;
}

interface SessionHistoryPanelProps {
  isOpen: boolean;
  onToggle: () => void;
  sessions: ChatSession[];
  onSessionSelect: (sessionId: string) => void;
  onSessionDelete: (sessionId: string) => void;
  currentSessionId?: string;
}

export function SessionHistoryPanel({
  isOpen,
  onToggle,
  sessions,
  onSessionSelect,
  onSessionDelete,
  currentSessionId
}: SessionHistoryPanelProps) {
  const [hoveredSession, setHoveredSession] = useState<string | null>(null);

  const formatRelativeTime = (date: Date) => {
    const now = new Date();
    const diffInHours = (now.getTime() - date.getTime()) / (1000 * 60 * 60);
    
    if (diffInHours < 1) return "Just now";
    if (diffInHours < 24) return `${Math.floor(diffInHours)}h ago`;
    if (diffInHours < 24 * 7) return `${Math.floor(diffInHours / 24)}d ago`;
    return date.toLocaleDateString();
  };

  const truncateText = (text: string, maxLength: number = 50) => {
    return text.length > maxLength ? text.substring(0, maxLength) + "..." : text;
  };

  return (
    <>
      {/* Toggle Button */}
      <Button
        variant="outline"
        size="sm"
        onClick={onToggle}
        className={cn(
          "fixed top-20 left-4 z-50 bg-card/90 backdrop-blur-sm border-border/50 shadow-lg transition-all duration-300",
          isOpen ? "translate-x-80" : "translate-x-0"
        )}
      >
        {isOpen ? (
          <ChevronLeft className="h-4 w-4" />
        ) : (
          <>
            <History className="h-4 w-4 mr-2" />
            <span className="hidden md:inline">History</span>
          </>
        )}
      </Button>

      {/* Sidebar Panel */}
      <div
        className={cn(
          "fixed top-0 left-0 h-full w-80 bg-background/95 backdrop-blur-sm border-r border-border/50 shadow-xl z-40 transition-transform duration-300 ease-out",
          isOpen ? "translate-x-0" : "-translate-x-full"
        )}
      >
        <div className="flex flex-col h-full">
          {/* Header */}
          <div className="flex-shrink-0 p-4 border-b border-border/50">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-3">
                <div className="p-2 bg-purple-500/20 rounded-lg border border-purple-500/30">
                  <History className="w-4 h-4 text-purple-400" />
                </div>
                <div>
                  <h2 className="font-semibold text-foreground">Session History</h2>
                  <p className="text-xs text-muted-foreground">
                    {sessions.length} {sessions.length === 1 ? 'session' : 'sessions'}
                  </p>
                </div>
              </div>
            </div>
          </div>

          {/* Sessions List */}
          <ScrollArea className="flex-1">
            <div className="p-4 space-y-3">
              {sessions.length === 0 ? (
                <div className="text-center py-8">
                  <div className="p-4 bg-muted/50 rounded-xl border border-border/50">
                    <MessageSquare className="w-8 h-8 text-muted-foreground mx-auto mb-3" />
                    <p className="text-sm text-muted-foreground">
                      No previous sessions
                    </p>
                    <p className="text-xs text-muted-foreground mt-1">
                      Start a research query to begin
                    </p>
                  </div>
                </div>
              ) : (
                sessions.map((session) => (
                  <Card
                    key={session.id}
                    className={cn(
                      "group cursor-pointer transition-all duration-200 hover:shadow-md",
                      currentSessionId === session.id 
                        ? "bg-blue-500/10 border-blue-500/30 shadow-blue-500/10" 
                        : "bg-card/50 border-border/50 hover:bg-card/80"
                    )}
                    onMouseEnter={() => setHoveredSession(session.id)}
                    onMouseLeave={() => setHoveredSession(null)}
                    onClick={() => onSessionSelect(session.id)}
                  >
                    <CardContent className="p-4">
                      <div className="flex items-start justify-between gap-3">
                        <div className="flex-1 min-w-0">
                          <div className="flex items-center gap-2 mb-2">
                            <Search className="w-3 h-3 text-blue-400 flex-shrink-0" />
                            <h3 className="font-medium text-sm text-foreground truncate">
                              {truncateText(session.title, 25)}
                            </h3>
                          </div>
                          
                          <p className="text-xs text-muted-foreground mb-2 line-clamp-2">
                            {truncateText(session.lastMessage, 60)}
                          </p>
                          
                          <div className="flex items-center justify-between text-xs text-muted-foreground">
                            <div className="flex items-center gap-1">
                              <Clock className="w-3 h-3" />
                              {formatRelativeTime(session.timestamp)}
                            </div>
                            <span className="flex items-center gap-1">
                              <MessageSquare className="w-3 h-3" />
                              {session.messageCount}
                            </span>
                          </div>
                        </div>
                        
                        {hoveredSession === session.id && (
                          <Button
                            variant="ghost"
                            size="sm"
                            className="h-6 w-6 p-0 text-red-400 hover:text-red-300 hover:bg-red-500/20 opacity-0 group-hover:opacity-100 transition-opacity duration-200"
                            onClick={(e) => {
                              e.stopPropagation();
                              onSessionDelete(session.id);
                            }}
                          >
                            <Trash2 className="h-3 w-3" />
                          </Button>
                        )}
                      </div>
                    </CardContent>
                  </Card>
                ))
              )}
            </div>
          </ScrollArea>

          {/* Footer */}
          <div className="flex-shrink-0 p-4 border-t border-border/50">
            <Button
              variant="outline"
              size="sm"
              className="w-full text-muted-foreground hover:text-foreground"
              onClick={() => {
                // Clear all sessions logic would go here
                console.log("Clear all sessions");
              }}
            >
              <Trash2 className="w-3 h-3 mr-2" />
              Clear All Sessions
            </Button>
          </div>
        </div>
      </div>

      {/* Overlay */}
      {isOpen && (
        <div
          className="fixed inset-0 bg-black/20 backdrop-blur-sm z-30 transition-opacity duration-300"
          onClick={onToggle}
        />
      )}
    </>
  );
}
