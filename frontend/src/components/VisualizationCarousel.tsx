import { useState, useEffect } from "react";
import { Button } from "@/components/ui/button";
import { ChevronLeft, ChevronRight, BarChart3 } from "lucide-react";
import { cn } from "@/lib/utils";

interface Visualization {
  type: string;
  format: string;
  base64_data: string;
  description: string;
}

interface VisualizationCarouselProps {
  visualizations: Visualization[];
  className?: string;
}

export function VisualizationCarousel({ 
  visualizations, 
  className 
}: VisualizationCarouselProps) {
  const [currentIndex, setCurrentIndex] = useState(0);

  if (!visualizations || visualizations.length === 0) {
    return null;
  }

  const goToPrevious = () => {
    setCurrentIndex((prevIndex) => 
      prevIndex === 0 ? visualizations.length - 1 : prevIndex - 1
    );
  };

  const goToNext = () => {
    setCurrentIndex((prevIndex) => 
      prevIndex === visualizations.length - 1 ? 0 : prevIndex + 1
    );
  };

  // Keyboard navigation
  useEffect(() => {
    const handleKeyDown = (event: KeyboardEvent) => {
      if (visualizations.length <= 1) return;
      
      if (event.key === 'ArrowLeft') {
        event.preventDefault();
        goToPrevious();
      } else if (event.key === 'ArrowRight') {
        event.preventDefault();
        goToNext();
      }
    };

    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [visualizations.length]);

  const currentViz = visualizations[currentIndex];

  return (
    <div className={cn("mt-6 space-y-4", className)}>
      {/* Header */}
      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center gap-2">
          <div className="p-1.5 bg-blue-500/20 rounded-lg border border-blue-500/30">
            <BarChart3 className="w-4 h-4 text-blue-400" />
          </div>
          <h4 className="font-semibold text-foreground text-sm">Data Visualizations</h4>
          {visualizations.length > 1 && (
            <span className="text-xs text-muted-foreground bg-muted/30 px-2 py-1 rounded-full">
              {currentIndex + 1} of {visualizations.length}
            </span>
          )}
        </div>
        
        {/* Navigation Controls */}
        {visualizations.length > 1 && (
          <div className="flex items-center gap-1">
            <Button
              variant="ghost"
              size="sm"
              onClick={goToPrevious}
              className="h-8 w-8 p-0 text-muted-foreground hover:text-foreground"
              title="Previous visualization"
            >
              <ChevronLeft className="h-4 w-4" />
            </Button>
            <Button
              variant="ghost"
              size="sm"
              onClick={goToNext}
              className="h-8 w-8 p-0 text-muted-foreground hover:text-foreground"
              title="Next visualization"
            >
              <ChevronRight className="h-4 w-4" />
            </Button>
          </div>
        )}
      </div>

      {/* Visualization Display */}
      <div className="bg-card/50 rounded-xl border border-border/50 p-4 backdrop-blur-sm">
        {currentViz.description && (
          <p className="text-sm text-muted-foreground mb-3">{currentViz.description}</p>
        )}
        
        <div className="flex justify-center">
          <img 
            src={`data:image/${currentViz.format || 'png'};base64,${currentViz.base64_data}`}
            alt={currentViz.description || `Visualization ${currentIndex + 1}`}
            className="max-w-full h-auto rounded-lg shadow-md border border-border/30 transition-all duration-300"
            style={{maxHeight: '400px'}}
          />
        </div>
      </div>

      {/* Dots Indicator (for multiple visualizations) */}
      {visualizations.length > 1 && (
        <div className="flex justify-center gap-2 mt-4">
          {visualizations.map((_, index) => (
            <button
              key={index}
              onClick={() => setCurrentIndex(index)}
              className={cn(
                "w-2 h-2 rounded-full transition-all duration-200",
                index === currentIndex 
                  ? "bg-blue-500 w-6" 
                  : "bg-muted-foreground/30 hover:bg-muted-foreground/50"
              )}
              title={`View visualization ${index + 1}`}
            />
          ))}
        </div>
      )}      {/* Keyboard Navigation Hint */}
      {visualizations.length > 1 && (
        <div className="text-xs text-muted-foreground text-center">
          Use arrow buttons, click dots, or press left/right arrow keys to navigate
        </div>
      )}
    </div>
  );
}
