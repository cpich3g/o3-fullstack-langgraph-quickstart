import { useState } from "react";
import { Button } from "@/components/ui/button";
import { SquarePen, Send, StopCircle } from "lucide-react";

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
        className={`flex flex-row items-center justify-between text-white rounded-2xl ${
          hasHistory ? "rounded-br-lg" : ""
        } break-words min-h-7 bg-white/[0.03] backdrop-blur-xl px-4 pt-3 shadow-lg hover:bg-white/[0.06] transition-all duration-300 ease-in-out relative overflow-hidden border border-white/[0.03]`}
      ><textarea
          value={internalInputValue}
          onChange={(e) => setInternalInputValue(e.target.value)}
          onKeyDown={handleInternalKeyDown}
          placeholder="Who won the Euro 2024 and scored the most goals?"
          className="w-full text-white/95 placeholder-white/60 resize-none !border-0 !focus:outline-none !focus:ring-0 !outline-none !focus-visible:ring-0 !shadow-none !bg-transparent md:text-base min-h-[56px] max-h-[200px] font-medium [&:not(:focus)]:bg-transparent [&:focus]:bg-transparent [&]:bg-transparent dark:[&]:bg-transparent"
          rows={1}
        />
        <div className="-mt-3">
          {isLoading ? (
            <Button
              type="button"
              variant="ghost"
              size="icon"
              className="text-red-500 hover:text-red-400 hover:bg-red-500/10 p-2 cursor-pointer rounded-full transition-all duration-200 shadow-sm"
              onClick={onCancel}
            >
              <StopCircle className="h-5 w-5" />
            </Button>
          ) : (            <Button
              type="submit"
              variant="ghost"
              className={`${
                isSubmitDisabled
                  ? "text-white/40"
                  : "text-blue-400 hover:text-blue-300 hover:bg-blue-500/20"
              } p-2 cursor-pointer rounded-full transition-all duration-300 text-base shadow-lg flex items-center gap-1.5 backdrop-blur-sm`}
              disabled={isSubmitDisabled}
            >
              <span className="text-sm font-semibold">Search</span>
              <Send className="h-4 w-4" />
            </Button>
          )}
        </div>
      </div>      {hasHistory && (
        <div className="flex items-center justify-end mt-2">
          <Button
            className="bg-white/[0.03] backdrop-blur-xl text-white/90 hover:bg-white/[0.06] hover:text-white cursor-pointer rounded-xl px-4 py-2 shadow-lg transition-all duration-300 flex items-center gap-2 border border-white/[0.03]"
            variant="outline"
            onClick={() => window.location.reload()}
          >
            <SquarePen size={16} />
            <span className="text-sm font-semibold">New Search</span>
          </Button>
        </div>
      )}
    </form>
  );
};
