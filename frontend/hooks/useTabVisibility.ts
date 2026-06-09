// useTabVisibility.ts
// Hook that returns true when the browser tab is active (visible)
import { useEffect, useState } from 'react';

export function useTabVisibility(): boolean {
  // Default to true (visible) on server/SSR where document is not available
  const [isVisible, setIsVisible] = useState(() =>
    typeof document !== 'undefined' ? !document.hidden : true
  );

  useEffect(() => {
    const handleVisibilityChange = () => setIsVisible(!document.hidden);
    document.addEventListener('visibilitychange', handleVisibilityChange);
    return () => document.removeEventListener('visibilitychange', handleVisibilityChange);
  }, []);

  return isVisible;
}
