import React, { useState, useEffect } from 'react';

interface TypingAnimationProps {
  className?: string;
}

export const TypingAnimation: React.FC<TypingAnimationProps> = ({ className = "" }) => {
  const [currentStep, setCurrentStep] = useState(0);
  const [currentText, setCurrentText] = useState("");
  const [isDeleting, setIsDeleting] = useState(false);
  
  const steps = [
    "Analyzing your request",
    "Searching for information", 
    "Processing research data",
    "Generating insights",
    "Preparing response"
  ];

  useEffect(() => {
    const currentFullText = steps[currentStep];
    const timeout = setTimeout(() => {
      if (!isDeleting) {
        // Typing forward
        if (currentText.length < currentFullText.length) {
          setCurrentText(currentFullText.slice(0, currentText.length + 1));
        } else {
          // Start deleting after a pause
          setTimeout(() => setIsDeleting(true), 1500);
        }
      } else {
        // Deleting
        if (currentText.length > 0) {
          setCurrentText(currentText.slice(0, -1));
        } else {
          // Move to next step
          setIsDeleting(false);
          setCurrentStep((prev) => (prev + 1) % steps.length);
        }
      }
    }, isDeleting ? 50 : 100); // Faster deletion, slower typing

    return () => clearTimeout(timeout);
  }, [currentText, currentStep, isDeleting, steps]);

  return (
    <div className={`flex items-center gap-3 ${className}`}>
      {/* Animated dots */}
      <div className="flex space-x-1">
        <div className="w-2 h-2 bg-blue-400 rounded-full animate-bounce"></div>
        <div className="w-2 h-2 bg-blue-400 rounded-full animate-bounce" style={{animationDelay: '0.1s'}}></div>
        <div className="w-2 h-2 bg-blue-400 rounded-full animate-bounce" style={{animationDelay: '0.2s'}}></div>
      </div>
      
      {/* Typing text */}
      <span className="text-lg text-foreground">
        {currentText}
        <span className="inline-block w-0.5 h-5 bg-blue-400 ml-1 animate-pulse"></span>
      </span>
    </div>
  );
};
