import React from 'react';
import { ExternalLink, CheckCircle, XCircle } from 'lucide-react';

interface Source {
  label: string;
  short_url: string;
  value: string;
  snippet: string;
  scraped_successfully?: boolean;
}

interface SourcesDisplayProps {
  sources: Source[];
}

export const SourcesDisplay: React.FC<SourcesDisplayProps> = ({ sources }) => {
  if (!sources || sources.length === 0) return null;
  return (
    <div className="bg-card rounded-lg border border-border overflow-hidden">
      <div className="px-4 py-3 bg-muted border-b border-border">
        <h4 className="font-semibold text-foreground flex items-center">
          <ExternalLink className="h-4 w-4 mr-2 text-blue-400" />
          Sources ({sources.length})
        </h4>
      </div>
      <div className="p-4">
        <div className="grid gap-3">
          {sources.map((source, index) => (            <div key={index} className="border border-border rounded-lg p-4 bg-muted/50 hover:bg-muted transition-all duration-300 hover:shadow-lg hover:shadow-blue-500/5 group">
              <div className="flex items-start justify-between">
                <a 
                  href={source.value} 
                  target="_blank" 
                  rel="noopener noreferrer"
                  className="inline-flex items-center gap-2 text-blue-400 hover:text-blue-300 font-medium text-sm leading-tight flex-1 mr-3 transition-all duration-300 group-hover:gap-2.5"
                >
                  <span className="truncate">{source.label}</span>
                  <ExternalLink className="h-3.5 w-3.5 opacity-60 group-hover:opacity-100 transition-all duration-300 flex-shrink-0 group-hover:scale-110" />
                </a>
                {source.scraped_successfully !== undefined && (
                  <div className="flex-shrink-0">
                    {source.scraped_successfully ? (
                      <div title="Content successfully analyzed" className="flex items-center">
                        <CheckCircle className="h-4 w-4 text-green-400" />
                      </div>
                    ) : (
                      <div title="Content not available" className="flex items-center">
                        <XCircle className="h-4 w-4 text-red-400" />
                      </div>
                    )}
                  </div>
                )}              </div>              {source.short_url && (
                <div className="mt-2 text-xs text-muted-foreground font-mono bg-muted/50 px-2 py-1 rounded">
                  {source.short_url}
                </div>
              )}
              {source.snippet && (
                <p className="text-xs text-muted-foreground mt-3 leading-relaxed line-clamp-3 bg-muted/30 p-2 rounded border-l-2 border-blue-500/20">
                  {source.snippet}
                </p>
              )}
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};
