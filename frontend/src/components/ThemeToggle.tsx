import { Button } from '@/components/ui/button';
import { useTheme } from '@/components/ThemeProvider';
import { Moon, Sun } from 'lucide-react';

interface ThemeToggleProps {
  className?: string;
}

export function ThemeToggle({ className = '' }: ThemeToggleProps) {
  const { theme, toggleTheme } = useTheme();

  return (
    <Button
      variant="ghost"
      size="icon"
      onClick={toggleTheme}
      className={`relative p-2 rounded-full transition-all duration-200 hover:bg-accent/60 ${className}`}
      title={`Switch to ${theme === 'light' ? 'dark' : 'light'} mode`}
    >
      <Sun 
        className={`h-4 w-4 transition-all duration-300 ${
          theme === 'light' 
            ? 'rotate-0 scale-100 text-foreground' 
            : 'rotate-90 scale-0 text-muted-foreground'
        }`}
      />
      <Moon 
        className={`absolute h-4 w-4 transition-all duration-300 ${
          theme === 'dark' 
            ? 'rotate-0 scale-100 text-foreground' 
            : '-rotate-90 scale-0 text-muted-foreground'
        }`}
      />
    </Button>
  );
}
