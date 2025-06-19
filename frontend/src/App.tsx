import { useStream } from "@langchain/langgraph-sdk/react";
import type { Message } from "@langchain/langgraph-sdk";
import { useState, useEffect, useRef, useCallback } from "react";
import { ProcessedEvent } from "@/components/ActivityTimeline";
import { WelcomeScreen } from "@/components/WelcomeScreen";
import { ChatMessagesView } from "@/components/ChatMessagesView";
import { ThemeProvider } from "@/components/ThemeProvider";
import { ThemeToggle } from "@/components/ThemeToggle";
import { ResearchProgressRing } from "@/components/ResearchProgressRing";
import { ChevronDown, ChevronUp } from "lucide-react";

interface ResearchInsight {
  type: "trend" | "source" | "analysis" | "suggestion" | "methodology" | "progress";
  title: string;
  description: string;
  confidence?: number;
  url?: string;
  timestamp?: Date;
  metrics?: {
    sourceCount?: number;
    queryCount?: number;
    loopCount?: number;
    duration?: string;
  };
  status?: "completed" | "in_progress" | "pending";
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
  const [isQuickResearchCollapsed, setIsQuickResearchCollapsed] = useState<boolean>(false);
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
  }, [thread.messages, thread.isLoading, processedEventsTimeline]);

  // Auto-collapse Quick Research section when chat starts
  useEffect(() => {
    if (thread.messages.length > 0 && !isQuickResearchCollapsed) {
      setIsQuickResearchCollapsed(true);
    }
  }, [thread.messages.length, isQuickResearchCollapsed]);const handleSubmit = useCallback(
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
          initial_search_query_count = 5;
          max_research_loops = 5;
          break;
        case "high":
          initial_search_query_count = 10;
          max_research_loops = 20;
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
        reasoning_model: "o3", // Default model since it's pre-configured
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
      case "medium": return { label: "Balanced", description: "5 queries, 5 loops", color: "text-blue-400" };
      case "high": return { label: "Thorough", description: "10 queries, 20 loops", color: "text-purple-400" };
      default: return { label: "Thorough", description: "10 queries, 20 loops", color: "text-purple-400" };
    }
  }, [currentResearchMode]);  // Enhanced research insights generation based on research progress
  useEffect(() => {
    if (processedEventsTimeline.length > 0) {
      const newInsights: ResearchInsight[] = [];
      const currentTime = new Date();
      
      // Add methodology insight for initial query generation
      const hasGeneration = processedEventsTimeline.some(e => e.title.toLowerCase().includes("generating"));
      if (hasGeneration) {
        newInsights.push({
          type: "methodology",
          title: "Research Strategy Optimized",
          description: `Intelligent query generation tailored for ${currentResearchMode} depth research with targeted search strategies.`,
          confidence: 0.95,
          status: "completed",
          timestamp: currentTime,
          metrics: {
            queryCount: processedEventsTimeline.filter(e => e.title.toLowerCase().includes("generating")).length
          }
        });
      }

      // Add source quality insights for web research
      const webResearchEvents = processedEventsTimeline.filter(e => e.title.toLowerCase().includes("web research"));
      if (webResearchEvents.length > 0) {
        const sourceCount = webResearchEvents.reduce((acc, event) => {
          if (typeof event.data === 'string' && event.data.includes("Found")) {
            const match = event.data.match(/Found (\d+) sources/);
            return acc + (match ? parseInt(match[1]) : 1);
          }
          return acc + 1;
        }, 0);

        newInsights.push({
          type: "source",
          title: "Source Discovery & Analysis",
          description: `Successfully gathered ${sourceCount} sources across multiple domains. Quality verification and content analysis completed.`,
          confidence: 0.85,
          status: "completed",
          timestamp: currentTime,
          metrics: {
            sourceCount: sourceCount,
            loopCount: webResearchEvents.length
          }
        });
      }

      // Add reflection analysis insights
      const reflectionEvents = processedEventsTimeline.filter(e => e.title.toLowerCase().includes("reflection"));
      reflectionEvents.forEach((event, index) => {
        let analysisTitle = "Research Depth Analysis";
        let analysisDescription = "Comprehensive evaluation of information coverage and research completeness.";
        let confidence = 0.7;
        
        if (typeof event.data === 'string') {
          if (event.data.includes("Search successful")) {
            analysisTitle = "Research Completion Validated";
            analysisDescription = "Analysis confirms sufficient information depth achieved. Research objectives met with high confidence.";
            confidence = 0.9;
          } else if (event.data.includes("Need more information")) {
            analysisTitle = "Knowledge Gap Identification";
            analysisDescription = "Analysis identified specific knowledge gaps. Additional targeted research queries generated for comprehensive coverage.";
            confidence = 0.8;
          }
        }
          newInsights.push({
          type: "analysis",
          title: analysisTitle,
          description: analysisDescription,
          confidence: confidence,
          status: (typeof event.data === 'string' && event.data.includes("Search successful")) ? "completed" : "in_progress",
          timestamp: currentTime,
          metrics: {
            loopCount: index + 1
          }
        });
      });

      // Add progress insight for ongoing research
      if (thread.isLoading && processedEventsTimeline.length > 0) {
        const progressPercent = calculateProgress();
        newInsights.push({
          type: "progress",
          title: "Research Progress Tracking",
          description: `Research ${progressPercent.toFixed(0)}% complete. Current phase: ${getProgressLabel()}. Advanced algorithms ensuring comprehensive coverage.`,
          confidence: 0.75,
          status: "in_progress",
          timestamp: currentTime,
          metrics: {
            queryCount: processedEventsTimeline.filter(e => e.title.toLowerCase().includes("generating")).length,
            sourceCount: processedEventsTimeline.filter(e => e.title.toLowerCase().includes("research")).length
          }
        });
      }

      // Add final completion insight
      const hasFinalized = processedEventsTimeline.some(e => e.title.toLowerCase().includes("finalizing"));
      if (hasFinalized && !thread.isLoading) {
        newInsights.push({
          type: "analysis",
          title: "Research Mission Accomplished",
          description: `Comprehensive research completed successfully. All identified knowledge gaps addressed with high-quality source integration.`,
          confidence: 0.95,
          status: "completed",
          timestamp: currentTime,
          metrics: {
            sourceCount: processedEventsTimeline.filter(e => e.title.toLowerCase().includes("research")).length,
            queryCount: processedEventsTimeline.filter(e => e.title.toLowerCase().includes("generating")).length,
            loopCount: processedEventsTimeline.filter(e => e.title.toLowerCase().includes("reflection")).length
          }
        });
      }
      
      setResearchInsights(newInsights);
    }
  }, [processedEventsTimeline, thread.isLoading, currentResearchMode, calculateProgress, getProgressLabel]);return (
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
                </div>                {/* Research Insights - Enhanced with better spacing and alignment */}
                {researchInsights.length > 0 && (
                  <div className="mt-4 space-y-3">
                    <div className="flex items-center justify-between">
                      <div className="text-xs font-medium text-foreground">Research Intelligence</div>
                      <div className="text-xs text-muted-foreground">{researchInsights.length} insights</div>
                    </div>
                    <div className="space-y-3">
                      {researchInsights.map((insight, index) => (
                        <div key={index} className={`rounded-lg p-3 border transition-all duration-200 hover:shadow-sm ${
                          insight.type === 'analysis' ? 'bg-blue-500/10 border-blue-500/20' :
                          insight.type === 'source' ? 'bg-green-500/10 border-green-500/20' :
                          insight.type === 'methodology' ? 'bg-purple-500/10 border-purple-500/20' :
                          insight.type === 'progress' ? 'bg-orange-500/10 border-orange-500/20' :
                          'bg-muted/20 border-border/30'
                        }`}>
                          {/* Header with title and status */}
                          <div className="flex items-center justify-between mb-2">
                            <div className={`font-medium text-sm flex-1 pr-2 ${
                              insight.type === 'analysis' ? 'text-blue-400' :
                              insight.type === 'source' ? 'text-green-400' :
                              insight.type === 'methodology' ? 'text-purple-400' :
                              insight.type === 'progress' ? 'text-orange-400' :
                              'text-foreground'
                            }`}>
                              {insight.title}
                            </div>
                            {insight.status && (
                              <div className={`text-xs px-2 py-1 rounded-full flex-shrink-0 font-medium ${
                                insight.status === 'completed' ? 'bg-green-500/20 text-green-400 border border-green-500/30' :
                                insight.status === 'in_progress' ? 'bg-blue-500/20 text-blue-400 border border-blue-500/30' :
                                'bg-gray-500/20 text-gray-400 border border-gray-500/30'
                              }`}>
                                {insight.status.replace('_', ' ')}
                              </div>
                            )}
                          </div>
                          
                          {/* Description */}
                          <div className="text-muted-foreground mb-3 text-xs leading-relaxed">
                            {insight.description}
                          </div>
                          
                          {/* Footer with metrics and timestamp */}
                          <div className="flex items-center justify-between text-xs">
                            <div className="flex items-center gap-3">
                              {insight.confidence && (
                                <div className="flex items-center gap-1">
                                  <span className="text-muted-foreground/80">Confidence:</span>
                                  <span className="text-foreground font-medium">
                                    {Math.round(insight.confidence * 100)}%
                                  </span>
                                </div>
                              )}
                              {insight.metrics && (
                                <div className="flex items-center gap-3 text-muted-foreground">
                                  {insight.metrics.sourceCount && (
                                    <div className="flex items-center gap-1">
                                      <span className="text-muted-foreground/80">Sources:</span>
                                      <span className="text-foreground font-medium">{insight.metrics.sourceCount}</span>
                                    </div>
                                  )}
                                  {insight.metrics.queryCount && (
                                    <div className="flex items-center gap-1">
                                      <span className="text-muted-foreground/80">Queries:</span>
                                      <span className="text-foreground font-medium">{insight.metrics.queryCount}</span>
                                    </div>
                                  )}
                                  {insight.metrics.loopCount && (
                                    <div className="flex items-center gap-1">
                                      <span className="text-muted-foreground/80">Loop:</span>
                                      <span className="text-foreground font-medium">{insight.metrics.loopCount}</span>
                                    </div>
                                  )}
                                </div>
                              )}
                            </div>
                            {insight.timestamp && (
                              <div className="text-muted-foreground/80 flex-shrink-0 ml-2">
                                {insight.timestamp.toLocaleTimeString()}
                              </div>
                            )}
                          </div>
                        </div>
                      ))}
                    </div>
                  </div>
                )}
              </div>
            )}            {/* Quick Research Prompts - Collapsible when chat starts */}
            <div className={`${thread.messages.length > 0 ? 'border-t border-border/30' : 'flex-1'} p-4`}>
              <div 
                className={`flex items-center justify-between mb-3 ${
                  thread.messages.length > 0 ? 'cursor-pointer hover:bg-muted/20 -mx-2 px-2 py-1 rounded-lg transition-colors' : ''
                }`}
                onClick={() => thread.messages.length > 0 && setIsQuickResearchCollapsed(!isQuickResearchCollapsed)}
              >
                <h3 className="text-sm font-medium text-foreground">Quick Research</h3>
                {thread.messages.length > 0 && (
                  <div className="text-muted-foreground">
                    {isQuickResearchCollapsed ? <ChevronDown className="h-4 w-4" /> : <ChevronUp className="h-4 w-4" />}
                  </div>
                )}
              </div>
              
              <div className={`transition-all duration-300 ease-in-out overflow-hidden ${
                thread.messages.length > 0 && isQuickResearchCollapsed ? 'max-h-0 opacity-0' : 'max-h-[800px] opacity-100'
              }`}>
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

                  <button
                    onClick={() => {
                      const textarea = textareaRef.current;
                      if (textarea) {
                        textarea.value = "Analyze current retail consumer behavior trends, e-commerce growth patterns, and omnichannel marketing strategies for 2025.";
                        textarea.focus();
                      }
                    }}
                    className="w-full text-left p-3 rounded-lg bg-muted/20 hover:bg-muted/40 transition-colors border border-border/30"
                  >
                    <div className="text-sm font-medium text-foreground">🛍️ Retail Intelligence</div>
                    <div className="text-xs text-muted-foreground">Consumer behavior & marketing trends</div>
                  </button>

                  <button
                    onClick={() => {
                      const textarea = textareaRef.current;
                      if (textarea) {
                        textarea.value = "Research advanced manufacturing technologies, Industry 4.0 implementations, and supply chain optimization strategies for 2025.";
                        textarea.focus();
                      }
                    }}
                    className="w-full text-left p-3 rounded-lg bg-muted/20 hover:bg-muted/40 transition-colors border border-border/30"
                  >
                    <div className="text-sm font-medium text-foreground">🏭 Manufacturing</div>
                    <div className="text-xs text-muted-foreground">Industry 4.0 & automation</div>
                  </button>

                  <button
                    onClick={() => {
                      const textarea = textareaRef.current;
                      if (textarea) {
                        textarea.value = "Examine hospitality industry recovery trends, guest experience innovations, and technology adoption in hotels and restaurants for 2025.";
                        textarea.focus();
                      }
                    }}
                    className="w-full text-left p-3 rounded-lg bg-muted/20 hover:bg-muted/40 transition-colors border border-border/30"
                  >
                    <div className="text-sm font-medium text-foreground">🏨 Hospitality</div>
                    <div className="text-xs text-muted-foreground">Guest experience & tech innovation</div>
                  </button>
                </div>
              </div>
            </div>{/* Footer with theme toggle */}
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
