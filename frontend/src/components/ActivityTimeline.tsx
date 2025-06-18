import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
} from "@/components/ui/card";
import { Progress } from "@/components/ui/progress";
import {
  Loader2,
  Activity,
  Info,
  Search,
  TextSearch,
  Brain,
  Pen,
  ChevronDown,
  ChevronUp,
} from "lucide-react";
import { useEffect, useState } from "react";
import { ResearchProgressRing } from "@/components/ResearchProgressRing";

export interface ProcessedEvent {
  title: string;
  data: string | string[] | Record<string, unknown>;
}

interface ActivityTimelineProps {
  processedEvents: ProcessedEvent[];
  isLoading: boolean;
}

export function ActivityTimeline({
  processedEvents,
  isLoading,
}: ActivityTimelineProps) {
  const [isTimelineCollapsed, setIsTimelineCollapsed] =
    useState<boolean>(false);
  const [expandedSteps, setExpandedSteps] = useState<Set<number>>(new Set());

  // Calculate progress based on research stages
  const calculateProgress = () => {
    if (!isLoading && processedEvents.length === 0) return 0;

    const stages = [
      "generating", // Query generation
      "research", // Web research
      "reflection", // Analysis
      "finalizing", // Answer synthesis
    ];

    let completedStages = 0;
    const totalStages = stages.length;

    // Check which stages have been completed
    stages.forEach((stage) => {
      const hasStage = processedEvents.some((event) =>
        event.title.toLowerCase().includes(stage)
      );
      if (hasStage) completedStages++;
    });

    // If currently loading and we have events, we're in progress on the next stage
    if (isLoading && processedEvents.length > 0) {
      // Add partial progress for the current stage being processed
      completedStages += 0.5;
    }

    // If research is complete (not loading and has events), show 100%
    if (!isLoading && processedEvents.length > 0) {
      return 100;
    }

    // Calculate percentage
    const percentage = (completedStages / totalStages) * 100;
    return Math.min(Math.max(percentage, isLoading ? 10 : 0), 100); // Clamp between 10 and 100
  };
  const getProgressLabel = () => {
    if (!isLoading && processedEvents.length === 0) return "Ready to research";
    if (!isLoading && processedEvents.length > 0) return "Research complete";

    // Determine current stage
    const hasGeneration = processedEvents.some((e) =>
      e.title.toLowerCase().includes("generating")
    );
    const hasResearch = processedEvents.some((e) =>
      e.title.toLowerCase().includes("research")
    );
    const hasReflection = processedEvents.some((e) =>
      e.title.toLowerCase().includes("reflection")
    );
    const hasFinalizing = processedEvents.some((e) =>
      e.title.toLowerCase().includes("finalizing")
    );

    if (hasFinalizing) return "Finalizing answer...";
    if (hasReflection) return "Analyzing results...";
    if (hasResearch) return "Gathering information...";
    if (hasGeneration) return "Planning research...";

    return "Initializing...";
  };

  const getEventIcon = (title: string, index: number) => {
    if (index === 0 && isLoading && processedEvents.length === 0) {
      return <Loader2 className="h-4 w-4 text-muted-foreground animate-spin" />;
    }

    const titleLower = title.toLowerCase();
    if (titleLower.includes("generating")) {
      return <TextSearch className="h-4 w-4 text-blue-400" />;
    } else if (titleLower.includes("thinking")) {
      return <Loader2 className="h-4 w-4 text-muted-foreground animate-spin" />;
    } else if (titleLower.includes("reflection")) {
      return <Brain className="h-4 w-4 text-purple-400" />;
    } else if (titleLower.includes("research")) {
      return <Search className="h-4 w-4 text-green-400" />;
    } else if (titleLower.includes("finalizing")) {
      return <Pen className="h-4 w-4 text-orange-400" />;
    }
    return <Activity className="h-4 w-4 text-muted-foreground" />;
  };

  const getCleanStepTitle = (title: string): string => {
    const titleLower = title.toLowerCase();

    if (titleLower.includes("generating")) {
      return "📝 Query Planning";
    }
    if (titleLower.includes("web research")) {
      return "🔍 Information Gathering";
    }
    if (titleLower.includes("reflection")) {
      return "🧠 Research Analysis";
    }
    if (titleLower.includes("finalizing")) {
      return "✨ Response Synthesis";
    }
    if (titleLower.includes("thinking")) {
      return "💭 Processing";
    }

    return title;
  };
  const getCleanStepDescription = (
    title: string,
    data: string | string[] | Record<string, unknown>
  ): string => {
    const titleLower = title.toLowerCase();

    // Generate cleaner descriptions based on the step type
    if (titleLower.includes("generating")) {
      if (Array.isArray(data)) {
        return `Generated ${data.length} search ${
          data.length === 1 ? "query" : "queries"
        } based on the research topic`;
      }
      if (typeof data === "object" && data !== null) {
        const dataObj = data as Record<string, unknown>;
        if (dataObj.query) {
          const queries = Array.isArray(dataObj.query)
            ? dataObj.query
            : [dataObj.query];
          return `Generated ${queries.length} targeted search ${
            queries.length === 1 ? "query" : "queries"
          } to gather comprehensive information`;
        }
      }
      return "Generated search queries to explore the topic comprehensively";
    }

    if (titleLower.includes("web research")) {
      if (typeof data === "string") {
        if (data.includes("Found") && data.includes("sources")) {
          return data; // Already well formatted
        }
        if (data.includes("AI-based")) {
          return "Conducted AI-powered analysis as external web search was not available";
        }
      }
      return "Conducted comprehensive web research to gather current information";
    }

    if (titleLower.includes("reflection")) {
      if (typeof data === "string") {
        if (data.includes("successful")) {
          return "Research analysis complete - sufficient information gathered to provide comprehensive answer";
        }
        if (data.includes("Need more")) {
          return "Analysis indicated need for additional focused research to ensure completeness";
        }
      }
      return "Evaluated research completeness and determined next steps";
    }

    if (titleLower.includes("finalizing")) {
      return "Synthesizing all research findings into a comprehensive, well-structured response";
    }

    if (titleLower.includes("thinking")) {
      return "Processing and analyzing available information to guide research strategy";
    }

    // For other cases, return the original data if it's a clean string
    if (typeof data === "string") {
      return data;
    }

    // For arrays, join them meaningfully
    if (Array.isArray(data)) {
      return data.join(", ");
    }

    // For objects, try to extract meaningful summary
    if (typeof data === "object" && data !== null) {
      const dataObj = data as Record<string, unknown>;
      if (dataObj.rationale && dataObj.query) {
        const queries = Array.isArray(dataObj.query)
          ? dataObj.query
          : [dataObj.query];
        return `Developed research strategy targeting: ${queries.join(", ")}`;
      }
    }

    return "Processing research step...";
  };
  const renderEventData = (eventItem: ProcessedEvent, index: number) => {
    // Get clean description instead of raw data
    const cleanDescription = getCleanStepDescription(
      eventItem.title,
      eventItem.data
    );
    const hasComplexData = typeof eventItem.data === "object" && eventItem.data !== null;
    const isExpanded = expandedSteps.has(index);

    // For query generation, show the structured view if it's object data with rationale and query
    if (typeof eventItem.data === "object" && eventItem.data !== null) {
      const data = eventItem.data as Record<string, unknown>;

      // Check if it's a query generation response - show detailed view for this important step
      if (data.rationale && data.query && eventItem.title.toLowerCase().includes("generating")) {
        return (
          <div className="space-y-2">
            <div className="text-xs text-foreground mb-2">{cleanDescription}</div>
            {isExpanded && (
              <>
                <div className="p-2 bg-muted/50 rounded-md border border-border/50">
                  <div className="text-xs font-medium text-foreground mb-1">Strategy:</div>
                  <div className="text-xs text-foreground">{String(data.rationale)}</div>
                </div>
                <div className="p-2 bg-blue-500/10 rounded-md border border-blue-500/20">
                  <div className="text-xs font-medium text-blue-300 mb-1">Search Terms:</div>
                  <div className="text-xs text-blue-200 font-mono">
                    {Array.isArray(data.query) ? data.query.join(", ") : String(data.query)}
                  </div>
                </div>
              </>
            )}
            <button
              onClick={(e) => {
                e.stopPropagation();
                setExpandedSteps(prev => {
                  const newExpanded = new Set(prev);
                  if (isExpanded) {
                    newExpanded.delete(index);
                  } else {
                    newExpanded.add(index);
                  }
                  return newExpanded;
                });
              }}
              className="text-xs text-blue-400 hover:text-blue-300 underline cursor-pointer"
            >
              {isExpanded ? "Hide details" : "Show details"}
            </button>
          </div>
        );
      }
    }
      return (
      <div>
        <div className="text-xs text-foreground">{cleanDescription}</div>
        {hasComplexData && !eventItem.title.toLowerCase().includes("generating") && (
          <button
            onClick={(e) => {
              e.stopPropagation();
              const newExpanded = new Set(expandedSteps);
              if (isExpanded) {
                newExpanded.delete(index);
              } else {
                newExpanded.add(index);
              }
              setExpandedSteps(newExpanded);
            }}
            className="text-xs text-muted-foreground hover:text-foreground underline cursor-pointer mt-1"
          >
            {isExpanded ? "Hide raw data" : "Show raw data"}
          </button>
        )}
        {hasComplexData && isExpanded && !eventItem.title.toLowerCase().includes("generating") && (
          <pre className="text-xs text-muted-foreground mt-2 p-2 bg-muted/50 rounded border border-border overflow-x-auto">
            {JSON.stringify(eventItem.data, null, 2)}
          </pre>
        )}
      </div>
    );
  };

  useEffect(() => {
    if (!isLoading && processedEvents.length !== 0) {
      setIsTimelineCollapsed(true);
    }
  }, [isLoading, processedEvents]);
  return (
    <Card className="border-none rounded-lg bg-card">
      <CardHeader>
        <CardDescription className="flex items-center justify-between">
          <div
            className="flex items-center justify-start text-sm w-full cursor-pointer gap-2 text-foreground"
            onClick={() => setIsTimelineCollapsed(!isTimelineCollapsed)}
          >
            <div className="flex items-center gap-2">
              🔬 Research Progress
              {!isLoading && processedEvents.length > 0 && (
                <span className="text-xs bg-green-500/20 text-green-400 px-2 py-0.5 rounded-full border border-green-500/30">
                  Complete
                </span>
              )}
              {isLoading && (
                <span className="text-xs bg-blue-500/20 text-blue-400 px-2 py-0.5 rounded-full border border-blue-500/30">
                  Active
                </span>
              )}
            </div>
            {isTimelineCollapsed ? (
              <ChevronDown className="h-4 w-4 mr-2" />
            ) : (
              <ChevronUp className="h-4 w-4 mr-2" />
            )}
          </div>        </CardDescription>
      </CardHeader>        {/* Progress Ring Section */}
      <div className="px-6 pb-4">
        <div className="flex items-center gap-4">
          <ResearchProgressRing 
            progress={calculateProgress()} 
            size="md"
            className="flex-shrink-0"
          >
            <div className="text-xs font-bold text-foreground">
              {Math.round(calculateProgress())}%
            </div>
          </ResearchProgressRing>
          
          <div className="flex-1 space-y-2">
            <div className="flex items-center justify-between">
              <span className="text-sm font-medium text-foreground">
                {getProgressLabel()}
              </span>
              <span className="text-xs text-muted-foreground">
                {processedEvents.length} {processedEvents.length === 1 ? 'step' : 'steps'}
              </span>
            </div>
            <Progress 
              value={calculateProgress()} 
              className="h-1.5 bg-muted/30"
            />
          </div>
        </div>
      </div>
        {!isTimelineCollapsed && (
        <CardContent>
          {isLoading && processedEvents.length === 0 && (
            <div className="relative pl-8 pb-4">
              <div className="absolute left-3 top-3.5 h-full w-0.5 bg-border" />
              <div className="absolute left-0.5 top-2 h-5 w-5 rounded-full bg-border flex items-center justify-center ring-4 ring-background">
                <Loader2 className="h-3 w-3 text-muted-foreground animate-spin" />
              </div>
              <div>
                <p className="text-sm text-foreground font-medium">
                  🚀 Initializing Research
                </p>
                <p className="text-xs text-muted-foreground">
                  Preparing to gather comprehensive information...
                </p>
              </div>
            </div>
          )}
          {processedEvents.length > 0 ? (
            <div className="space-y-0">
              {processedEvents.map((eventItem, index) => (
                <div key={index} className="relative pl-8 pb-4">
                  {index < processedEvents.length - 1 ||
                  (isLoading && index === processedEvents.length - 1) ? (
                    <div className="absolute left-3 top-3.5 h-full w-0.5 bg-border" />
                  ) : null}
                  <div className="absolute left-0.5 top-2 h-6 w-6 rounded-full bg-muted flex items-center justify-center ring-4 ring-card">
                    {getEventIcon(eventItem.title, index)}
                  </div>
                  <div>
                    <p className="text-sm text-foreground font-medium mb-0.5">
                      {getCleanStepTitle(eventItem.title)}
                    </p>
                    <p className="text-xs text-foreground leading-relaxed">
                      {renderEventData(eventItem, index)}
                    </p>
                  </div>
                </div>
              ))}
              {isLoading && processedEvents.length > 0 && (
                <div className="relative pl-8 pb-4">
                  <div className="absolute left-0.5 top-2 h-5 w-5 rounded-full bg-muted flex items-center justify-center ring-4 ring-card">
                    <Loader2 className="h-3 w-3 text-muted-foreground animate-spin" />
                  </div>
                  <div>
                    <p className="text-sm text-foreground font-medium">
                      🔄 Processing...
                    </p>
                  </div>
                </div>
              )}
              {/* Research completion summary */}
              {!isLoading && processedEvents.length > 0 && (
                <div className="relative pl-8 pb-2">
                  <div className="absolute left-0.5 top-2 h-5 w-5 rounded-full bg-green-500/20 flex items-center justify-center ring-4 ring-card border border-green-500/30">
                    <svg
                      className="h-3 w-3 text-green-400"
                      fill="currentColor"
                      viewBox="0 0 20 20"
                    >
                      <path
                        fillRule="evenodd"
                        d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z"
                        clipRule="evenodd"
                      />
                    </svg>
                  </div>
                  <div>
                    <p className="text-sm text-green-400 font-medium">
                      ✅ Research Complete
                    </p>
                    <p className="text-xs text-muted-foreground">
                      {processedEvents.length} research{" "}
                      {processedEvents.length === 1 ? "step" : "steps"} completed
                      successfully
                    </p>
                  </div>
                </div>
              )}
            </div>
          ) : !isLoading ? ( // Only show "No activity" if not loading and no events
            <div className="flex flex-col items-center justify-center h-full text-muted-foreground pt-10">
              <Info className="h-6 w-6 mb-3" />
              <p className="text-sm">No activity to display.</p>
              <p className="text-xs text-muted-foreground mt-1">
                Timeline will update during processing.
              </p>
            </div>
          ) : null}
        </CardContent>
      )}
    </Card>
  );
}
