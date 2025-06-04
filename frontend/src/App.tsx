import { useStream } from "@langchain/langgraph-sdk/react";
import type { Message } from "@langchain/langgraph-sdk";
import { useState, useEffect, useRef, useCallback } from "react";
import { ProcessedEvent } from "@/components/ActivityTimeline";
import { WelcomeScreen } from "@/components/WelcomeScreen";
import { ChatMessagesView } from "@/components/ChatMessagesView";
import { ThemeProvider } from "@/components/ThemeProvider";

export default function App() {
  const [processedEventsTimeline, setProcessedEventsTimeline] = useState<
    ProcessedEvent[]
  >([]);
  const [historicalActivities, setHistoricalActivities] = useState<
    Record<string, ProcessedEvent[]>
  >({});
  const scrollAreaRef = useRef<HTMLDivElement>(null);
  const hasFinalizeEventOccurredRef = useRef(false);

  const thread = useStream<{
    messages: Message[];
    initial_search_query_count: number;
    max_research_loops: number;
    reasoning_model: string;
  }>({
    apiUrl: import.meta.env.DEV
      ? "http://localhost:2024"
      : "http://localhost:8123",
    assistantId: "agent",
    messagesKey: "messages",    // eslint-disable-next-line @typescript-eslint/no-explicit-any
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
    },
  });

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

  const handleSubmit = useCallback(
    (submittedInputValue: string, effort: string, model: string) => {
      if (!submittedInputValue.trim()) return;
      setProcessedEventsTimeline([]);
      hasFinalizeEventOccurredRef.current = false;

      // convert effort to, initial_search_query_count and max_research_loops
      // low means max 1 loop and 1 query
      // medium means max 3 loops and 3 queries
      // high means max 10 loops and 5 queries
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
          initial_search_query_count = 5;
          max_research_loops = 10;
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
        reasoning_model: model,
      });
    },
    [thread]
  );

  const handleCancel = useCallback(() => {
    thread.stop();
    window.location.reload();
  }, [thread]);  return (
    <ThemeProvider>
      <div className="fixed inset-0 bg-gradient-to-br from-background via-muted/30 to-background text-foreground font-sans antialiased">
        <main className="flex flex-col h-full max-w-6xl mx-auto">
          {thread.messages.length === 0 ? (
            <div className="flex flex-col h-full">
              <WelcomeScreen
                handleSubmit={handleSubmit}
                isLoading={thread.isLoading}
                onCancel={handleCancel}
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
            />
          )}
        </main>
      </div>
    </ThemeProvider>
  );
}
