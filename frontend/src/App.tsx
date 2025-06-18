import { useStream } from "@langchain/langgraph-sdk/react";
import type { Message } from "@langchain/langgraph-sdk";
import { useState, useEffect, useRef, useCallback } from "react";
import { ProcessedEvent } from "@/components/ActivityTimeline";
import { WelcomeScreen } from "@/components/WelcomeScreen";
import { ChatMessagesView } from "@/components/ChatMessagesView";
import { ThemeProvider } from "@/components/ThemeProvider";
import { ThemeToggle } from "@/components/ThemeToggle";
import { ResearchProgressRing } from "@/components/ResearchProgressRing";

interface ResearchInsight {
  type: "trend" | "source" | "analysis" | "suggestion";
  title: string;
  description: string;
  confidence?: number;
  url?: string;
  timestamp?: Date;
}

export default function App() {
  const [processedEventsTimeline, setProcessedEventsTimeline] = useState<
    ProcessedEvent[]
  >([]);
  const [historicalActivities, setHistoricalActivities] = useState<
    Record<string, ProcessedEvent[]>
  >({});
  const [researchInsights, setResearchInsights] = useState<ResearchInsight[]>([]);
  const [currentResearchMode, setCurrentResearchMode] = useState<string>("medium");
  const scrollAreaRef = useRef<HTMLDivElement>(null);
  const hasFinalizeEventOccurredRef = useRef(false);
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  const thread = useStream<{
    messages: Message[];
    initial_search_query_count: number;
    max_research_loops: number;
    reasoning_model: string;
  }>({
    apiUrl: import.meta.env.DEV
      ? "http://localhost:2024"
      : "http://localhost:8000",
    assistantId: "agent",
    messagesKey: "messages",// eslint-disable-next-line @typescript-eslint/no-explicit-any
    onFinish: (event: any) => {
      console.log(event);
    },
    // eslint-disable-next-line @typescript-eslint/no-explicit-any
    onUpdateEvent: (event: any) => {
      console.log("Event received:", event); // Debug log to understand actual structure
      let processedEvent: ProcessedEvent | null = null;
      
      // The generate_query node in LangGraph returns { query_list: [...] }
      // So the event structure should be { generate_query: { query_list: [...] } }
      if (event.generate_query) {
        // Access query_list from the generate_query node result
        const nodeOutput = event.generate_query;
        const queryList = nodeOutput.query_list || nodeOutput; // Fallback to nodeOutput itself
        let queryData = "Generating search queries...";
        
        if (Array.isArray(queryList)) {
          queryData = queryList.join(", ");
        } else if (typeof queryList === 'string') {
          queryData = queryList;
        } else if (queryList && typeof queryList === 'object' && queryList.query_list) {
          // If the structure is nested differently
          const nestedList = queryList.query_list;
          if (Array.isArray(nestedList)) {
            queryData = nestedList.join(", ");
          } else {
            queryData = String(nestedList);
          }
        } else if (queryList) {
          queryData = String(queryList);
        }
        
        processedEvent = {
          title: "Generating Search Queries",
          data: queryData,
        };
      } else if (event.web_research) {
        const sources = event.web_research.sources_gathered || [];
        const numSources = sources.length;
        const uniqueLabels = [
          ...new Set(sources.map((s: {label?: string}) => s.label).filter(Boolean)),
        ];
        const exampleLabels = uniqueLabels.slice(0, 3).join(", ");
        const scrapedCount = sources.filter((s: {scraped_successfully?: boolean}) => s.scraped_successfully).length;
        
        processedEvent = {
          title: "Web Research",
          data: numSources > 0 
            ? `Found ${numSources} sources${scrapedCount > 0 ? ` (${scrapedCount} analyzed)` : ''}. Related to: ${exampleLabels || "N/A"}.`
            : "AI-based research (no external sources)",
        };      } else if (event.reflection) {
        let reflectionData = "Reflecting on research results...";
        
        if (event.reflection.is_sufficient) {
          reflectionData = "Search successful, generating final answer.";
        } else {
          const followUpQueries = event.reflection.follow_up_queries;
          if (Array.isArray(followUpQueries)) {
            reflectionData = `Need more information, searching for ${followUpQueries.join(", ")}`;
          } else if (typeof followUpQueries === 'string') {
            reflectionData = `Need more information, searching for ${followUpQueries}`;
          } else {
            reflectionData = "Need more information, continuing research...";
          }
        }
        
        processedEvent = {
          title: "Reflection",
          data: reflectionData,
        };
      } else if (event.finalize_answer) {
        processedEvent = {
          title: "Finalizing Answer",
          data: "Composing and presenting the final answer.",
        };
        hasFinalizeEventOccurredRef.current = true;
      }
      if (processedEvent) {
        setProcessedEventsTimeline((prevEvents) => [
          ...prevEvents,
          processedEvent!,
        ]);
      }
    },  });

  useEffect(() => {
    if (scrollAreaRef.current) {
      const scrollViewport = scrollAreaRef.current.querySelector(
        "[data-radix-scroll-area-viewport]"
      );
      if (scrollViewport) {
        scrollViewport.scrollTop = scrollViewport.scrollHeight;
      }
    }
  }, [thread.messages]);

  useEffect(() => {
    if (
      hasFinalizeEventOccurredRef.current &&
      !thread.isLoading &&
      thread.messages.length > 0
    ) {
      const lastMessage = thread.messages[thread.messages.length - 1];
      if (lastMessage && lastMessage.type === "ai" && lastMessage.id) {
        setHistoricalActivities((prev) => ({
          ...prev,
          [lastMessage.id!]: [...processedEventsTimeline],
        }));
      }
      hasFinalizeEventOccurredRef.current = false;
    }
  }, [thread.messages, thread.isLoading, processedEventsTimeline]);  const handleSubmit = useCallback(
    (submittedInputValue: string, effort: string) => {
      if (!submittedInputValue.trim()) return;
      setProcessedEventsTimeline([]);
      setCurrentResearchMode(effort);
      hasFinalizeEventOccurredRef.current = false;

      let initial_search_query_count = 0;
      let max_research_loops = 0;
      switch (effort) {
        case "low":
          initial_search_query_count = 1;
          max_research_loops = 1;
          break;
        case "medium":
          initial_search_query_count = 3;
          max_research_loops = 3;
          break;
        case "high":
          initial_search_query_count = 10;
          max_research_loops = 30;
          break;
      }

      const newMessages: Message[] = [
        ...(thread.messages || []),
        {
          type: "human",
          content: submittedInputValue,
          id: Date.now().toString(),
        },
      ];
      thread.submit({
        messages: newMessages,
        initial_search_query_count: initial_search_query_count,
        max_research_loops: max_research_loops,
        reasoning_model: "gpt-4o", // Default model since it's pre-configured
      });
    },
    [thread]
  );  const handleCancel = useCallback(() => {
    thread.stop();
    window.location.reload();
  }, [thread]);

  // Calculate research progress based on events
  const calculateProgress = useCallback(() => {
    if (!thread.isLoading && processedEventsTimeline.length === 0) return 0;
    
    const expectedSteps = ['Planning', 'Research', 'Analysis', 'Report'];
    const completedSteps = processedEventsTimeline.filter(event => 
      expectedSteps.some(step => event.title.toLowerCase().includes(step.toLowerCase()))
    ).length;
    
    if (!thread.isLoading && processedEventsTimeline.length > 0) return 100;
    return Math.min((completedSteps / expectedSteps.length) * 100, 90);
  }, [thread.isLoading, processedEventsTimeline]);

  const getProgressLabel = useCallback(() => {
    if (!thread.isLoading && processedEventsTimeline.length === 0) return "Ready";
    if (!thread.isLoading) return "Research Complete";
    
    const progress = calculateProgress();
    if (progress < 25) return "Planning Research";
    if (progress < 50) return "Gathering Sources";
    if (progress < 75) return "Analyzing Data";
    return "Generating Report";
  }, [thread.isLoading, calculateProgress]);

  const getResearchModeLabel = useCallback(() => {
    switch (currentResearchMode) {
      case "low": return { label: "Quick", description: "1 query, 1 loop", color: "text-green-400" };
      case "medium": return { label: "Balanced", description: "3 queries, 3 loops", color: "text-blue-400" };
      case "high": return { label: "Thorough", description: "10 queries, 30 loops", color: "text-purple-400" };
      default: return { label: "Balanced", description: "3 queries, 3 loops", color: "text-blue-400" };
    }
  }, [currentResearchMode]);

  // Generate sample insights based on research progress
  useEffect(() => {
    if (processedEventsTimeline.length > 0) {
      const newInsights: ResearchInsight[] = [];
      
      processedEventsTimeline.forEach((event, index) => {
        if (event.title.toLowerCase().includes("research")) {
          newInsights.push({
            type: "source",
            title: "Quality Sources Found",
            description: "Research has identified several high-quality sources for comprehensive analysis.",
            confidence: 0.8,
            timestamp: new Date()
          });
        }
        
        if (event.title.toLowerCase().includes("reflection") && index > 0) {
          newInsights.push({
            type: "analysis",
            title: "Research Analysis",
            description: "Initial research analysis suggests the need for additional focused queries.",
            confidence: 0.7,
            timestamp: new Date()
          });
        }
      });
      
      setResearchInsights(newInsights);
    }
  }, [processedEventsTimeline]);  return (
    <ThemeProvider>
      <div className="fixed inset-0 bg-gradient-to-br from-background via-muted/30 to-background text-foreground font-sans antialiased">
        {/* Full-width desktop layout */}
        <div className="flex h-full">
          {/* Left sidebar for research progress and quick actions */}
          <div className="w-80 flex-shrink-0 flex flex-col bg-card/30 border-r border-border/30">            {/* Header */}
            <div className="p-4 border-b border-border/30">
              <div className="flex items-center gap-3 mb-3">
                <div className="relative">
                  <div className="absolute inset-0 bg-gradient-to-r from-blue-500/20 to-indigo-500/20 rounded-lg blur-sm"></div>                  <div className="relative p-2 bg-gradient-to-r from-blue-500/10 to-indigo-500/10 rounded-lg border border-blue-500/30">
                    <img 
                      src="/dr_logo.png" 
                      alt="Deep Research Logo" 
                      className="w-8 h-8 object-cover rounded"
                    />
                  </div>
                </div>
                <div>
                  <h1 className="text-lg font-bold text-foreground">Deep Research</h1>
                  <p className="text-xs text-muted-foreground">AI-powered research assistant</p>
                </div>
              </div>
            </div>{/* Research Progress Section */}
            {(thread.isLoading || processedEventsTimeline.length > 0) && (
              <div className="p-4 border-b border-border/30">
                <div className="flex items-center justify-between mb-3">
                  <h3 className="text-sm font-medium text-foreground">Research Progress</h3>
                  <div className={`px-2 py-1 rounded text-xs font-medium ${getResearchModeLabel().color} bg-muted/20 border border-border/30`}>
                    {getResearchModeLabel().label}
                  </div>
                </div>
                
                <div className="flex items-center gap-4 mb-4">
                  <ResearchProgressRing 
                    progress={calculateProgress()} 
                    size="md"
                    className="flex-shrink-0"
                  >
                    <div className="text-xs font-bold text-foreground">
                      {Math.round(calculateProgress())}%
                    </div>
                  </ResearchProgressRing>
                  
                  <div className="flex-1">
                    <div className="text-sm font-medium text-foreground mb-1">
                      {getProgressLabel()}
                    </div>
                    <div className="text-xs text-muted-foreground mb-1">
                      {processedEventsTimeline.length} {processedEventsTimeline.length === 1 ? 'step' : 'steps'} completed
                    </div>
                    <div className="text-xs text-muted-foreground">
                      Mode: {getResearchModeLabel().description}
                    </div>
                  </div>
                </div>

                {/* Recent activity */}
                {processedEventsTimeline.length > 0 && (
                  <div className="space-y-2">
                    <div className="text-xs text-muted-foreground">Recent Activity:</div>
                    <div className="space-y-1 max-h-24 overflow-y-auto scrollbar-thin">
                      {processedEventsTimeline.slice(-3).map((event, index) => (
                        <div key={index} className="text-xs bg-muted/20 rounded p-2">
                          <div className="font-medium text-foreground">{event.title}</div>
                        </div>
                      ))}
                    </div>
                  </div>
                )}

                {/* Research Insights */}
                {researchInsights.length > 0 && (
                  <div className="mt-4 space-y-2">
                    <div className="text-xs text-muted-foreground">Research Insights:</div>
                    <div className="space-y-1 max-h-32 overflow-y-auto scrollbar-thin">
                      {researchInsights.slice(-3).map((insight, index) => (
                        <div key={index} className="text-xs bg-blue-500/10 rounded p-2 border border-blue-500/20">
                          <div className="font-medium text-blue-400 mb-1">{insight.title}</div>
                          <div className="text-muted-foreground">{insight.description}</div>
                          {insight.confidence && (
                            <div className="text-xs text-blue-300 mt-1">
                              {Math.round(insight.confidence * 100)}% confidence
                            </div>
                          )}
                        </div>
                      ))}
                    </div>
                  </div>                )}
              </div>
            )}

            {/* Quick Research Prompts */}
            <div className="flex-1 p-4">
              <h3 className="text-sm font-medium text-foreground mb-3">Quick Research</h3>
              <div className="space-y-2">
                <button
                  onClick={() => {
                    const textarea = textareaRef.current;
                    if (textarea) {
                      textarea.value = "What are the latest trends in artificial intelligence and machine learning for 2025?";
                      textarea.focus();
                    }
                  }}
                  className="w-full text-left p-3 rounded-lg bg-muted/20 hover:bg-muted/40 transition-colors border border-border/30"
                >
                  <div className="text-sm font-medium text-foreground">🤖 AI Trends 2025</div>
                  <div className="text-xs text-muted-foreground">Latest AI and ML developments</div>
                </button>
                
                <button
                  onClick={() => {
                    const textarea = textareaRef.current;
                    if (textarea) {
                      textarea.value = "Analyze the current state of the global cryptocurrency market and blockchain adoption trends.";
                      textarea.focus();
                    }
                  }}
                  className="w-full text-left p-3 rounded-lg bg-muted/20 hover:bg-muted/40 transition-colors border border-border/30"
                >
                  <div className="text-sm font-medium text-foreground">📈 Crypto Market</div>
                  <div className="text-xs text-muted-foreground">Blockchain and DeFi analysis</div>
                </button>
                
                <button
                  onClick={() => {
                    const textarea = textareaRef.current;
                    if (textarea) {
                      textarea.value = "Research the latest developments in renewable energy technology and sustainability initiatives.";
                      textarea.focus();
                    }
                  }}
                  className="w-full text-left p-3 rounded-lg bg-muted/20 hover:bg-muted/40 transition-colors border border-border/30"
                >
                  <div className="text-sm font-medium text-foreground">🌱 Clean Energy</div>
                  <div className="text-xs text-muted-foreground">Sustainability and green tech</div>
                </button>
                
                <button
                  onClick={() => {
                    const textarea = textareaRef.current;
                    if (textarea) {
                      textarea.value = "Explore the impact of remote work on productivity and company culture in 2025.";
                      textarea.focus();
                    }
                  }}
                  className="w-full text-left p-3 rounded-lg bg-muted/20 hover:bg-muted/40 transition-colors border border-border/30"
                >
                  <div className="text-sm font-medium text-foreground">💼 Future of Work</div>
                  <div className="text-xs text-muted-foreground">Remote work trends</div>
                </button>
              </div>
            </div>            {/* Footer with theme toggle */}
            <div className="p-4 border-t border-border/30 flex justify-between items-center">
              <div className="text-xs text-muted-foreground">AI Research Tool</div>
              <ThemeToggle />
            </div>
          </div>

          {/* Main content area */}
          <main className="flex-1 flex flex-col min-w-0">
            {thread.messages.length === 0 ? (
              <div className="flex flex-col h-full">
                <WelcomeScreen
                  handleSubmit={handleSubmit}
                  isLoading={thread.isLoading}
                  onCancel={handleCancel}
                  textareaRef={textareaRef}
                />
              </div>
            ) : (
              <ChatMessagesView
                messages={thread.messages}
                isLoading={thread.isLoading}
                scrollAreaRef={scrollAreaRef}
                onSubmit={handleSubmit}
                onCancel={handleCancel}
                liveActivityEvents={processedEventsTimeline}
                historicalActivities={historicalActivities}
                textareaRef={textareaRef}
              />            )}
          </main>
        </div>
      </div>
    </ThemeProvider>
  );
}
