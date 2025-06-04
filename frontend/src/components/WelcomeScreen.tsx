import { InputForm } from "./InputForm";
import { ThemeToggle } from "./ThemeToggle";

interface WelcomeScreenProps {
  handleSubmit: (
    submittedInputValue: string,
    effort: string,
    model: string
  ) => void;
  onCancel: () => void;
  isLoading: boolean;
}

export const WelcomeScreen: React.FC<WelcomeScreenProps> = ({
  handleSubmit,
  onCancel,
  isLoading,
}) => {
  const handleInputSubmit = (inputValue: string) => {
    // Use default values for effort and model when called from InputForm
    handleSubmit(inputValue, "standard", "gpt-4o");
  };
  return (
    <div className="flex flex-col items-center justify-center text-center px-6 flex-1 w-full max-w-5xl mx-auto gap-8 relative">
      {/* Theme Toggle in top-right corner */}
      <div className="absolute top-6 right-6 z-10">
        <ThemeToggle />
      </div>        {/* Banner Image */}
      <div className="w-full max-w-4xl mx-auto mb-4">
        <div className="relative group">
          <div className="absolute inset-0 bg-gradient-to-r from-blue-500/10 via-purple-500/10 to-indigo-500/10 rounded-2xl blur-xl opacity-70 group-hover:opacity-100 transition-opacity duration-500"></div>
          <div className="relative bg-card/20 backdrop-blur-sm rounded-2xl border border-border/30 p-4 shadow-lg hover:shadow-m transition-all duration-300">
            <img 
              src="public/deep-banner.png" 
              alt="Deep Research Banner" 
              className="w-full h-max max-h-24 md:max-h-32 lg:max-h-36 object-cover rounded-xl drop-shadow-lg hover:drop-shadow-m transition-all duration-300"
            />
          </div>
        </div>
      </div>
      
      <div className="space-y-6">
        <div className="space-y-4">
          <h1 className="text-4xl md:text-6xl lg:text-7xl font-bold bg-gradient-to-r from-foreground via-foreground/90 to-foreground/80 bg-clip-text text-transparent">
            Deep Research
          </h1>
          <div className="space-y-3">
            {/* <p className="text-xl md:text-2xl text-muted-foreground leading-relaxed max-w-3xl mx-auto">
              Unlock comprehensive insights with intelligent research automation
            </p> */}
            <p className="text-lg md:text-xl text-muted-foreground/80 leading-relaxed max-w-2xl mx-auto">
              Ask complex questions and get thoroughly researched answers with cited sources
            </p>
          </div>
        </div>
        
        {/* Feature Highlights */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 max-w-4xl mx-auto mt-8">
          <div className="flex items-center gap-3 p-4 bg-card/30 rounded-xl border border-border/40 backdrop-blur-sm">
            <div className="p-2 bg-blue-500/20 rounded-lg">
              <svg className="w-5 h-5 text-blue-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
              </svg>
            </div>
            <div className="text-left">
              <div className="text-sm font-semibold text-foreground">Multi-Source Research</div>
              <div className="text-xs text-muted-foreground">Comprehensive web analysis</div>
            </div>
          </div>
          
          <div className="flex items-center gap-3 p-4 bg-card/30 rounded-xl border border-border/40 backdrop-blur-sm">
            <div className="p-2 bg-green-500/20 rounded-lg">
              <svg className="w-5 h-5 text-green-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4M7.835 4.697a3.42 3.42 0 001.946-.806 3.42 3.42 0 014.438 0 3.42 3.42 0 001.946.806 3.42 3.42 0 013.138 3.138 3.42 3.42 0 00.806 1.946 3.42 3.42 0 010 4.438 3.42 3.42 0 00-.806 1.946 3.42 3.42 0 01-3.138 3.138 3.42 3.42 0 00-1.946.806 3.42 3.42 0 01-4.438 0 3.42 3.42 0 00-1.946-.806 3.42 3.42 0 01-3.138-3.138 3.42 3.42 0 00-.806-1.946 3.42 3.42 0 010-4.438 3.42 3.42 0 00.806-1.946 3.42 3.42 0 013.138-3.138z" />
              </svg>
            </div>
            <div className="text-left">
              <div className="text-sm font-semibold text-foreground">Verified Sources</div>
              <div className="text-xs text-muted-foreground">Fact-checked information</div>
            </div>
          </div>
          
          <div className="flex items-center gap-3 p-4 bg-card/30 rounded-xl border border-border/40 backdrop-blur-sm">
            <div className="p-2 bg-purple-500/20 rounded-lg">
              <svg className="w-5 h-5 text-purple-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" />
              </svg>
            </div>
            <div className="text-left">
              <div className="text-sm font-semibold text-foreground">AI-Powered</div>
              <div className="text-xs text-muted-foreground">Azure agentic reasoning</div>
            </div>
          </div>
        </div>
      </div>
      <div className="w-full mt-6 max-w-3xl">
        <InputForm
          onSubmit={handleInputSubmit}
          isLoading={isLoading}
          onCancel={onCancel}
          hasHistory={false}
        />
      </div>
      <p className="text-sm text-muted-foreground mt-4 flex items-center gap-2">
        <svg className="w-4 h-4 text-blue-400" fill="currentColor" viewBox="0 0 20 20">
          <path d="M9.049 2.927c.3-.921 1.603-.921 1.902 0l1.07 3.292a1 1 0 00.95.69h3.462c.969 0 1.371 1.24.588 1.81l-2.8 2.034a1 1 0 00-.364 1.118l1.07 3.292c.3.921-.755 1.688-1.54 1.118l-2.8-2.034a1 1 0 00-1.175 0l-2.8 2.034c-.784.57-1.838-.197-1.539-1.118l1.07-3.292a1 1 0 00-.364-1.118L2.98 8.72c-.783-.57-.38-1.81.588-1.81h3.461a1 1 0 00.951-.69l1.07-3.292z" />
        </svg>
        Powered by Azure AI and LangGraph.
      </p>
    </div>
  );
};
