import type React from "react";
import type { Message } from "@langchain/langgraph-sdk";
import { ScrollArea } from "@/components/ui/scroll-area";
import { Loader2, Copy, CopyCheck } from "lucide-react";
import { InputForm } from "@/components/InputForm";
import { Button } from "@/components/ui/button";
import { useState } from "react";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import { cn } from "@/lib/utils";
import { SourcesDisplay } from "@/components/SourcesDisplay";
import { ThemeToggle } from "@/components/ThemeToggle";
import {
  ActivityTimeline,
  ProcessedEvent,
} from "@/components/ActivityTimeline";

// Define types for structured message content
interface StructuredMessageContent {
  sources?: Array<{
    label: string;
    short_url: string;
    value: string;
    snippet: string;
    scraped_successfully?: boolean;
  }>;
  research_summary?: {
    total_queries: number;
    research_loops: number;
    sources_found: number;
    research_steps?: Array<{
      step: number;
      type: string;
      description: string;
      status: string;
    }>;
  };
}

// Helper function to check if additional_kwargs contains structured content
const getStructuredContent = (message: Message): StructuredMessageContent | null => {
  const messageWithKwargs = message as Record<string, unknown>;
  if (messageWithKwargs.additional_kwargs && typeof messageWithKwargs.additional_kwargs === 'object') {
    return messageWithKwargs.additional_kwargs as StructuredMessageContent;
  }
  return null;
};

// Markdown components with modern styling
const mdComponents = {
  h1: ({ className, children, ...props }: React.ComponentPropsWithoutRef<"h1">) => (
    <h1 className={cn("text-2xl font-bold mt-6 mb-3 text-foreground", className)} {...props}>
      {children}
    </h1>
  ),
  h2: ({ className, children, ...props }: React.ComponentPropsWithoutRef<"h2">) => (
    <h2 className={cn("text-xl font-semibold mt-5 mb-3 text-foreground", className)} {...props}>
      {children}
    </h2>
  ),
  h3: ({ className, children, ...props }: React.ComponentPropsWithoutRef<"h3">) => (
    <h3 className={cn("text-lg font-semibold mt-4 mb-2 text-foreground", className)} {...props}>
      {children}
    </h3>
  ),
  p: ({ className, children, ...props }: React.ComponentPropsWithoutRef<"p">) => (
    <p className={cn("mb-4 leading-relaxed text-foreground", className)} {...props}>
      {children}
    </p>
  ),
  a: ({ className, children, href, ...props }: React.ComponentPropsWithoutRef<"a">) => (
    <a
      className={cn(
        "inline-flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-gradient-to-r from-blue-500/10 to-indigo-500/10 text-blue-400 hover:text-blue-300 hover:from-blue-500/20 hover:to-indigo-500/20 transition-all duration-300 font-medium border border-blue-500/20 hover:border-blue-400/40 hover:shadow-lg hover:shadow-blue-500/10 group relative overflow-hidden",
        className
      )}
      href={href}
      target="_blank"
      rel="noopener noreferrer"
      {...props}
    >
      <span className="relative z-10">{children}</span>
      <svg 
        className="w-3.5 h-3.5 opacity-60 group-hover:opacity-100 transition-all duration-300 group-hover:scale-110 relative z-10" 
        fill="none" 
        stroke="currentColor" 
        viewBox="0 0 24 24"
      >
        <path 
          strokeLinecap="round" 
          strokeLinejoin="round" 
          strokeWidth={2} 
          d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14" 
        />
      </svg>
      <div className="absolute inset-0 bg-gradient-to-r from-blue-500/5 to-indigo-500/5 opacity-0 group-hover:opacity-100 transition-opacity duration-300" />
    </a>
  ),  ul: ({ className, children, ...props }: React.ComponentPropsWithoutRef<"ul">) => (
    <ul className={cn("list-disc pl-6 mb-4 space-y-1", className)} {...props}>
      {children}
    </ul>
  ),
  ol: ({ className, children, ...props }: React.ComponentPropsWithoutRef<"ol">) => (
    <ol className={cn("list-decimal pl-6 mb-4 space-y-1", className)} {...props}>
      {children}
    </ol>
  ),
  li: ({ className, children, ...props }: React.ComponentPropsWithoutRef<"li">) => (
    <li className={cn("text-foreground", className)} {...props}>
      {children}
    </li>
  ),
  blockquote: ({ className, children, ...props }: React.ComponentPropsWithoutRef<"blockquote">) => (
    <blockquote
      className={cn(
        "border-l-4 border-blue-500 pl-4 py-2 italic my-4 bg-muted/50 rounded-r text-muted-foreground",
        className
      )}
      {...props}
    >
      {children}
    </blockquote>
  ),
  code: ({ className, children, ...props }: React.ComponentPropsWithoutRef<"code">) => (
    <code
      className={cn(
        "bg-muted border border-border rounded px-1.5 py-0.5 font-mono text-sm text-foreground",
        className
      )}
      {...props}
    >
      {children}
    </code>
  ),
  pre: ({ className, children, ...props }: React.ComponentPropsWithoutRef<"pre">) => (
    <pre
      className={cn(
        "bg-muted border border-border p-4 rounded-lg overflow-x-auto font-mono text-sm my-4 text-foreground",
        className
      )}
      {...props}
    >
      {children}
    </pre>
  ),
  hr: ({ className, ...props }: React.ComponentPropsWithoutRef<"hr">) => (
    <hr className={cn("border-border my-4", className)} {...props} />
  ),  table: ({ className, children, ...props }: React.ComponentPropsWithoutRef<"table">) => (
    <div className="my-6 overflow-x-auto rounded-lg border border-border bg-card/50">
      <table className={cn("w-full border-collapse", className)} {...props}>
        {children}
      </table>
    </div>
  ),
  thead: ({ className, children, ...props }: React.ComponentPropsWithoutRef<"thead">) => (
    <thead className={cn("bg-muted", className)} {...props}>
      {children}
    </thead>
  ),
  tbody: ({ className, children, ...props }: React.ComponentPropsWithoutRef<"tbody">) => (
    <tbody className={cn("divide-y divide-border", className)} {...props}>
      {children}
    </tbody>
  ),
  tr: ({ className, children, ...props }: React.ComponentPropsWithoutRef<"tr">) => (
    <tr className={cn("hover:bg-muted/50 transition-colors", className)} {...props}>
      {children}
    </tr>
  ),
  th: ({ className, children, ...props }: React.ComponentPropsWithoutRef<"th">) => (
    <th
      className={cn(
        "px-4 py-3 text-left font-semibold text-foreground bg-muted first:rounded-tl-lg last:rounded-tr-lg border-r border-border last:border-r-0",
        className
      )}
      {...props}
    >
      {children}
    </th>
  ),
  td: ({ className, children, ...props }: React.ComponentPropsWithoutRef<"td">) => (
    <td
      className={cn(
        "px-4 py-3 text-foreground border-r border-border last:border-r-0 bg-card/30",
        className
      )}
      {...props}
    >
      {children}
    </td>
  ),
};

// Props for HumanMessageBubble
interface HumanMessageBubbleProps {
  message: Message;
  mdComponents: typeof mdComponents;
}

// ResearchSummary Component for Sidebar
interface ResearchSummaryProps {
  researchSummary: {
    total_queries: number;
    research_loops: number;
    sources_found: number;
    research_steps?: Array<{
      step: number;
      type: string;
      description: string;
      status: string;
    }>;
  };
}

const ResearchSummary: React.FC<ResearchSummaryProps> = ({ researchSummary }) => {
  if (!researchSummary) return null;

  return (
    <div className="mb-6">
      <div className="flex items-center gap-2 mb-4">
        <div className="p-1.5 bg-blue-500/20 rounded-lg border border-blue-500/30">
          <svg className="w-4 h-4 text-blue-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5H7a2 2 0 00-2 2v10a2 2 0 002 2h2m0 0h2a2 2 0 002-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2" />
          </svg>
        </div>        <h4 className="font-semibold text-foreground text-sm">Research Summary</h4>
      </div>
      
      {/* Compact Statistics Grid */}
      <div className="grid grid-cols-1 gap-3 mb-4">
        <div className="flex items-center gap-2 p-3 bg-card/50 rounded-xl border border-border/50 backdrop-blur-sm">
          <div className="p-1.5 bg-green-500/20 rounded-lg border border-green-500/30">
            <svg className="w-3 h-3 text-green-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
            </svg>
          </div>
          <div className="flex-1">
            <div className="text-sm font-bold text-foreground">{researchSummary.total_queries}</div>
            <div className="text-xs text-muted-foreground">Search Queries</div>
          </div>
        </div>
        
        <div className="flex items-center gap-2 p-3 bg-card/50 rounded-xl border border-border/50 backdrop-blur-sm">
          <div className="p-1.5 bg-purple-500/20 rounded-lg border border-purple-500/30">
            <svg className="w-3 h-3 text-purple-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
            </svg>
          </div>
          <div className="flex-1">
            <div className="text-sm font-bold text-foreground">{researchSummary.research_loops}</div>
            <div className="text-xs text-muted-foreground">Research Loops</div>
          </div>
        </div>
        
        <div className="flex items-center gap-2 p-3 bg-card/50 rounded-xl border border-border/50 backdrop-blur-sm">
          <div className="p-1.5 bg-blue-500/20 rounded-lg border border-blue-500/30">
            <svg className="w-3 h-3 text-blue-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13.828 10.172a4 4 0 00-5.656 0l-4 4a4 4 0 105.656 5.656l1.102-1.101m-.758-4.899a4 4 0 005.656 0l4-4a4 4 0 00-5.656-5.656l-1.1 1.1" />
            </svg>
          </div>
          <div className="flex-1">
            <div className="text-sm font-bold text-foreground">{researchSummary.sources_found}</div>
            <div className="text-xs text-muted-foreground">Sources Found</div>
          </div>
        </div>
      </div>

      {/* Research Steps */}
      {researchSummary.research_steps && researchSummary.research_steps.length > 0 && (
        <div className="mb-4">          <h5 className="text-xs font-semibold text-foreground mb-3 flex items-center gap-2">
            <svg className="w-3 h-3 text-blue-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4M7.835 4.697a3.42 3.42 0 001.946-.806 3.42 3.42 0 014.438 0 3.42 3.42 0 001.946.806 3.42 3.42 0 013.138 3.138 3.42 3.42 0 00.806 1.946 3.42 3.42 0 010 4.438 3.42 3.42 0 00-.806 1.946 3.42 3.42 0 01-3.138 3.138 3.42 3.42 0 00-1.946.806 3.42 3.42 0 01-4.438 0 3.42 3.42 0 00-1.946-.806 3.42 3.42 0 01-3.138-3.138 3.42 3.42 0 00-.806-1.946 3.42 3.42 0 010-4.438 3.42 3.42 0 00.806-1.946 3.42 3.42 0 013.138-3.138z" />
            </svg>
            Research Steps
          </h5>
          <div className="space-y-2">
            {researchSummary.research_steps.map((step: {
              step: number;
              type: string;
              description: string;
              status: string;
            }, index: number) => (
              <div key={index} className="flex items-start gap-2 p-3 bg-muted/50 rounded-xl border border-border/40 backdrop-blur-sm hover:bg-muted/60 transition-all duration-200">
                <div className="flex-shrink-0 mt-0.5">
                  <div className={`w-5 h-5 rounded-full flex items-center justify-center text-xs font-semibold transition-all duration-200 ${
                    step.status === 'completed' 
                      ? 'bg-green-500/20 text-green-400 border border-green-500/30 shadow-sm shadow-green-500/10' 
                      : 'bg-muted/20 text-muted-foreground border border-border/30'
                  }`}>
                    {step.status === 'completed' ? (
                      <svg className="w-2.5 h-2.5" fill="currentColor" viewBox="0 0 20 20">
                        <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
                      </svg>
                    ) : (
                      step.step
                    )}
                  </div>
                </div>
                <div className="flex-1 min-w-0">
                  <div className="flex items-center gap-1 mb-1">                    <span className={`inline-flex items-center px-2 py-0.5 rounded-full text-xs font-medium border transition-all duration-200 ${
                      step.type === 'search' 
                        ? 'bg-blue-500/20 text-blue-400 border-blue-500/30' 
                        : step.type === 'analysis'
                        ? 'bg-purple-500/20 text-purple-400 border-purple-500/30'
                        : 'bg-muted/20 text-muted-foreground border-border/30'
                    }`}>
                      {step.type === 'search' && (
                        <svg className="w-2.5 h-2.5 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
                        </svg>
                      )}
                      {step.type === 'analysis' && (
                        <svg className="w-2.5 h-2.5 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
                        </svg>
                      )}
                      {step.type.charAt(0).toUpperCase() + step.type.slice(1)}
                    </span>
                  </div>                  <p className="text-xs text-foreground leading-relaxed">{step.description}</p>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Completion Status */}
      <div className="p-3 bg-muted/40 rounded-xl border border-border/40 backdrop-blur-sm">
        <div className="flex items-center gap-2 text-xs text-muted-foreground">
          <svg className="w-3 h-3 text-green-400" fill="currentColor" viewBox="0 0 20 20">
            <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
          </svg>
          <span className="font-medium">Research completed successfully</span>
        </div>
      </div>
    </div>
  );
};

// Props for HumanMessageBubble
interface HumanMessageBubbleProps {
  message: Message;
  mdComponents: typeof mdComponents;
}

// HumanMessageBubble Component
const HumanMessageBubble: React.FC<HumanMessageBubbleProps> = ({
  message,
  mdComponents,
}) => {
  // Custom markdown components for white text in user message bubble
  const humanMessageMdComponents = {
    ...mdComponents,
    p: ({ className, children, ...props }: React.ComponentPropsWithoutRef<"p">) => (
      <p className={cn("mb-4 leading-relaxed text-white", className)} {...props}>
        {children}
      </p>
    ),
    h1: ({ className, children, ...props }: React.ComponentPropsWithoutRef<"h1">) => (
      <h1 className={cn("text-2xl font-bold mt-6 mb-3 text-white", className)} {...props}>
        {children}
      </h1>
    ),
    h2: ({ className, children, ...props }: React.ComponentPropsWithoutRef<"h2">) => (
      <h2 className={cn("text-xl font-semibold mt-5 mb-3 text-white", className)} {...props}>
        {children}
      </h2>
    ),
    h3: ({ className, children, ...props }: React.ComponentPropsWithoutRef<"h3">) => (
      <h3 className={cn("text-lg font-semibold mt-4 mb-2 text-white", className)} {...props}>
        {children}
      </h3>
    ),
    li: ({ className, children, ...props }: React.ComponentPropsWithoutRef<"li">) => (
      <li className={cn("text-white", className)} {...props}>
        {children}
      </li>
    ),
    strong: ({ className, children, ...props }: React.ComponentPropsWithoutRef<"strong">) => (
      <strong className={cn("text-white font-semibold", className)} {...props}>
        {children}
      </strong>
    ),
    em: ({ className, children, ...props }: React.ComponentPropsWithoutRef<"em">) => (
      <em className={cn("text-white/90", className)} {...props}>
        {children}
      </em>
    ),
    code: ({ className, children, ...props }: React.ComponentPropsWithoutRef<"code">) => (
      <code
        className={cn(
          "bg-white/20 border border-white/30 rounded px-1.5 py-0.5 font-mono text-sm text-white",
          className
        )}
        {...props}
      >
        {children}
      </code>
    ),
    blockquote: ({ className, children, ...props }: React.ComponentPropsWithoutRef<"blockquote">) => (
      <blockquote
        className={cn(
          "border-l-4 border-white/50 pl-4 py-2 italic my-4 bg-white/10 rounded-r text-white/90",
          className
        )}
        {...props}
      >
        {children}
      </blockquote>
    ),
  };

  return (
    <div className="bg-gradient-to-r from-primary to-primary/80 text-white rounded-2xl px-6 py-4 shadow-lg border border-primary/30 backdrop-blur-sm">
      <ReactMarkdown components={humanMessageMdComponents} remarkPlugins={[remarkGfm]}>
        {typeof message.content === "string"
          ? message.content
          : JSON.stringify(message.content)}
      </ReactMarkdown>
    </div>
  );
};

// Props for AiMessageBubble
interface AiMessageBubbleProps {
  message: Message;
  mdComponents: typeof mdComponents;
  handleCopy: (text: string, messageId: string) => void;
  copiedMessageId: string | null;
}

// AiMessageBubble Component
const AiMessageBubble: React.FC<AiMessageBubbleProps> = ({
  message,
  mdComponents,
  handleCopy,
  copiedMessageId,
}) => {
  // Get structured content from additional_kwargs
  const structuredContent = getStructuredContent(message);
  
  const displayContent = typeof message.content === "string" 
    ? message.content 
    : JSON.stringify(message.content);

  const copyContent = typeof message.content === "string" 
    ? message.content 
    : JSON.stringify(message.content);

  return (
    <div className="relative break-words flex flex-col max-w-none">
      {/* Main Content */}      <div className="bg-gradient-to-br from-card to-muted rounded-2xl p-6 border border-border/50 shadow-xl backdrop-blur-sm">
        <ReactMarkdown components={mdComponents} remarkPlugins={[remarkGfm]}>
          {displayContent}
        </ReactMarkdown>
      </div>
        {/* Sources Display */}
      {structuredContent && structuredContent.sources && structuredContent.sources.length > 0 && (
        <div className="mt-6">
          <SourcesDisplay sources={structuredContent.sources} />
        </div>
      )}{/* Copy Button */}
      <div className="flex justify-end mt-6">        <Button
          variant="outline"
          size="sm"
          className="text-muted-foreground hover:text-foreground border-border/40 hover:border-border/60 bg-card/50 hover:bg-muted/60 backdrop-blur-sm transition-all duration-200 shadow-sm hover:shadow-md"
          onClick={() => handleCopy(copyContent, message.id!)}
        >
          {copiedMessageId === message.id ? (
            <>
              <CopyCheck className="h-3.5 w-3.5 mr-2 text-green-400" />
              <span className="text-xs font-medium">Copied</span>
            </>
          ) : (
            <>
              <Copy className="h-3.5 w-3.5 mr-2" />
              <span className="text-xs font-medium">Copy Response</span>
            </>
          )}
        </Button>
      </div>
    </div>
  );
};

interface ChatMessagesViewProps {
  messages: Message[];
  isLoading: boolean;
  scrollAreaRef: React.RefObject<HTMLDivElement | null>;
  onSubmit: (inputValue: string, effort: string, model: string) => void;
  onCancel: () => void;
  liveActivityEvents: ProcessedEvent[];
  historicalActivities: Record<string, ProcessedEvent[]>;
}

export function ChatMessagesView({
  messages,
  isLoading,
  scrollAreaRef,
  onSubmit,
  onCancel,
  liveActivityEvents,
  historicalActivities,
}: ChatMessagesViewProps) {
  const [copiedMessageId, setCopiedMessageId] = useState<string | null>(null);

  const handleCopy = async (text: string, messageId: string) => {
    try {
      await navigator.clipboard.writeText(text);
      setCopiedMessageId(messageId);
      setTimeout(() => setCopiedMessageId(null), 2000); // Reset after 2 seconds
    } catch (err) {
      console.error("Failed to copy text: ", err);
    }
  };

  // Get research summary from the last AI message
  const getLastResearchSummary = () => {
    const lastAiMessage = messages
      .slice()
      .reverse()
      .find(msg => msg.type === "ai");
    
    if (lastAiMessage) {
      const structuredContent = getStructuredContent(lastAiMessage);
      return structuredContent?.research_summary;
    }
    return null;
  };

  const lastResearchSummary = getLastResearchSummary();

  return (    <div className="flex flex-col h-full relative">
      {/* Header/Title Area - Fixed */}      <div className="flex-shrink-0 p-4 border-b border-border/50 bg-background/95 backdrop-blur-sm">
        <div className="max-w-7xl mx-auto">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <div className="p-2 bg-gradient-to-r from-blue-500/20 to-indigo-500/20 rounded-lg border border-blue-500/30">
                <svg className="w-5 h-5 text-blue-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z" />
                </svg>
              </div>
              <div>
                <h1 className="text-xl font-bold text-foreground">AI Research Assistant</h1>
                <p className="text-sm text-muted-foreground">Powered by Azure AI</p>
              </div>
            </div>
            <ThemeToggle />
          </div>
        </div>
      </div>{/* Two-Column Layout - Scrollable */}
      <div className="flex-1 relative overflow-hidden">
        <div className="flex h-full max-w-7xl mx-auto">
          {/* Left Column - Chat Messages */}
          <div className="flex-1 min-w-0 pr-4">
            <ScrollArea className="h-full" ref={scrollAreaRef}>
              <div className="p-6 space-y-6 py-8">                {messages.map((message, index) => {
                  return (
                    <div key={message.id || `msg-${index}`} className="space-y-4">
                      <div
                        className={`flex items-start ${
                          message.type === "human" ? "justify-end" : "justify-start"
                        }`}
                      >
                        {message.type === "human" ? (
                          <div className="max-w-[80%]">
                            <HumanMessageBubble
                              message={message}
                              mdComponents={mdComponents}
                            />
                          </div>
                        ) : (
                          <div className="max-w-[95%] w-full">
                            <AiMessageBubble
                              message={message}
                              mdComponents={mdComponents}
                              handleCopy={handleCopy}
                              copiedMessageId={copiedMessageId}
                            />
                          </div>
                        )}
                      </div>
                    </div>
                  );
                })}

                {isLoading &&
                  (messages.length === 0 ||
                    messages[messages.length - 1].type === "human") && (
                    <div className="flex items-start mt-6">                      <div className="relative group max-w-[95%] w-full rounded-2xl p-6 shadow-xl break-words bg-gradient-to-br from-card to-muted text-foreground border border-border/50 backdrop-blur-sm min-h-[80px]">
                        <div className="flex items-center justify-start h-full">
                          <Loader2 className="h-6 w-6 animate-spin text-blue-400 mr-3" />
                          <span className="text-lg text-foreground">Processing your request...</span>
                        </div>
                      </div>
                    </div>
                  )}
              </div>
            </ScrollArea>
          </div>

          {/* Right Column - Research Progress */}          <div className="w-80 flex-shrink-0 border-l border-border/50 bg-background/30 backdrop-blur-sm">
            <div className="h-full flex flex-col">
              {/* Research Progress Header */}
              <div className="flex-shrink-0 p-4 border-b border-border/50">
                <div className="flex items-center gap-3">
                  <div className="p-2 bg-purple-500/20 rounded-lg border border-purple-500/30">
                    <svg className="w-4 h-4 text-purple-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" />
                    </svg>
                  </div>
                  <div>
                    <h3 className="text-sm font-semibold text-foreground">Research Progress</h3>
                    <p className="text-xs text-muted-foreground">Real-time analysis</p>
                  </div>
                </div>
              </div>{/* Research Progress Content */}
              <div className="flex-1 overflow-hidden">
                <ScrollArea className="h-full">
                  <div className="p-4">
                    {/* Research Summary */}
                    {lastResearchSummary && (
                      <ResearchSummary researchSummary={lastResearchSummary} />
                    )}

                    {/* Show live activity if loading */}
                    {isLoading && liveActivityEvents.length > 0 && (
                      <div className="mb-4">
                        <div className="flex items-center gap-2 mb-3">
                          <div className="p-1.5 bg-yellow-500/20 rounded-lg border border-yellow-500/30">
                            <svg className="w-4 h-4 text-yellow-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" />
                            </svg>
                          </div>                          <h4 className="font-semibold text-foreground text-sm">Live Activity</h4>
                        </div>
                        <ActivityTimeline
                          processedEvents={liveActivityEvents}
                          isLoading={true}
                        />
                      </div>
                    )}

                    {/* Show historical activity for the last AI message */}
                    {messages.length > 0 && 
                      messages[messages.length - 1].type === "ai" && 
                      historicalActivities[messages[messages.length - 1].id!] && 
                      historicalActivities[messages[messages.length - 1].id!].length > 0 && (
                      <div className="mb-4">
                        <div className="flex items-center gap-2 mb-3">
                          <div className="p-1.5 bg-green-500/20 rounded-lg border border-green-500/30">
                            <svg className="w-4 h-4 text-green-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4M7.835 4.697a3.42 3.42 0 001.946-.806 3.42 3.42 0 014.438 0 3.42 3.42 0 001.946.806 3.42 3.42 0 013.138 3.138 3.42 3.42 0 00.806 1.946 3.42 3.42 0 010 4.438 3.42 3.42 0 00-.806 1.946 3.42 3.42 0 01-3.138 3.138 3.42 3.42 0 00-1.946.806 3.42 3.42 0 01-4.438 0 3.42 3.42 0 00-1.946-.806 3.42 3.42 0 01-3.138-3.138 3.42 3.42 0 00-.806-1.946 3.42 3.42 0 010-4.438 3.42 3.42 0 00.806-1.946 3.42 3.42 0 013.138-3.138z" />
                            </svg>
                          </div>
                          <h4 className="font-semibold text-foreground text-sm">Activity Timeline</h4>
                        </div>
                        <ActivityTimeline
                          processedEvents={historicalActivities[messages[messages.length - 1].id!]}
                          isLoading={false}
                        />
                      </div>
                    )}

                    {/* Empty state */}
                    {!isLoading && 
                      !lastResearchSummary &&
                      (messages.length === 0 || 
                        (messages[messages.length - 1].type === "ai" && 
                          (!historicalActivities[messages[messages.length - 1].id!] || 
                           historicalActivities[messages[messages.length - 1].id!].length === 0))) && (
                      <div className="text-center py-8">                        <div className="p-4 bg-muted/50 rounded-xl border border-border/50 backdrop-blur-sm">
                          <svg className="w-8 h-8 text-muted-foreground mx-auto mb-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z" />
                          </svg>
                          <p className="text-sm text-muted-foreground">Research progress will appear here during analysis</p>
                        </div>
                      </div>
                    )}
                  </div>
                </ScrollArea>
              </div>
            </div>
          </div>
        </div>
      </div>      {/* Input Area - Fixed at bottom */}
      <div className="flex-shrink-0 border-t border-border/50 bg-background/90 backdrop-blur-sm">
        <InputForm
          onSubmit={(inputValue: string) => onSubmit(inputValue, "", "")}
          isLoading={isLoading}
          onCancel={onCancel}
          hasHistory={messages.length > 0}
        />
      </div>
    </div>
  );
}
