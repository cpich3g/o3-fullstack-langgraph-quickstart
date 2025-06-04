import { useState } from "react";
import { Button } from "@/components/ui/button";
import { Send, StopCircle, Plus } from "lucide-react";

interface InputFormProps {
  onSubmit: (inputValue: string) => void;
  onCancel: () => void;
  isLoading: boolean;
  hasHistory: boolean;
}

export const InputForm: React.FC<InputFormProps> = ({
  onSubmit,
  onCancel,
  isLoading,
  hasHistory,
}) => {
  const [internalInputValue, setInternalInputValue] = useState("");

  const handleInternalSubmit = (e?: React.FormEvent) => {
    if (e) e.preventDefault();
    if (!internalInputValue.trim()) return;
    onSubmit(internalInputValue);
    setInternalInputValue("");
  };

  const handleInternalKeyDown = (
    e: React.KeyboardEvent<HTMLTextAreaElement>
  ) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleInternalSubmit();
    }
  };

  const isSubmitDisabled = !internalInputValue.trim() || isLoading;

  return (    <form
      onSubmit={handleInternalSubmit}
      className="flex flex-col gap-3 px-4 py-2 bg-transparent"
    >      <div
        className={`flex flex-row items-end gap-3 text-white rounded-2xl ${
          hasHistory ? "rounded-br-lg" : ""
        } bg-white/[0.05] backdrop-blur-xl px-4 py-3 shadow-lg hover:bg-white/[0.08] focus-within:bg-white/[0.08] transition-all duration-200 ease-in-out border border-white/[0.08]`}
      >        <textarea
          value={internalInputValue}
          onChange={(e) => setInternalInputValue(e.target.value)}
          onKeyDown={handleInternalKeyDown}
          placeholder="Ask anything you'd like to research..."
          className="flex-1 text-white/90 placeholder-white/50 resize-none border-0 outline-0 bg-transparent text-base leading-6 py-2 min-h-[24px] max-h-[120px] font-normal placeholder:font-light"
          rows={1}
        />        <div className="flex-shrink-0 flex items-center gap-2">
          {hasHistory && (
            <Button
              type="button"
              variant="ghost"
              size="icon"
              className="text-white/60 hover:text-white/80 hover:bg-white/10 p-2 rounded-full transition-all duration-200"
              onClick={() => window.location.reload()}
              title="New Search"
            >
              <Plus className="h-4 w-4" />
            </Button>
          )}
          {isLoading ? (
            <Button
              type="button"
              variant="ghost"
              size="icon"
              className="text-red-500 hover:text-red-400 hover:bg-red-500/10 p-2 rounded-full transition-all duration-200"
              onClick={onCancel}
            >
              <StopCircle className="h-5 w-5" />
            </Button>
          ) : (
            <Button
              type="submit"
              variant="ghost"
              className={`${
                isSubmitDisabled
                  ? "text-white/40 cursor-not-allowed"
                  : "text-blue-400 hover:text-blue-300 hover:bg-blue-500/20"
              } p-2 rounded-full transition-all duration-200 flex items-center gap-1.5`}
              disabled={isSubmitDisabled}
            >
              <span className="text-sm font-medium">Search</span>
              <Send className="h-4 w-4" />
            </Button>
          )}
        </div>      </div>
    </form>
  );
};
