// RealtimeContext.tsx
import { createContext, useContext, ReactNode } from 'react';
import { useTabVisibility } from '../hooks/useTabVisibility';

type RealtimeContextValue = {
  /**
   * When false, polling effects (unread‑logs, blockchain watchers) should pause.
   * Currently tied to browser tab visibility, but can be extended.
   */
  enablePolling: boolean;
};

const RealtimeContext = createContext<RealtimeContextValue>({ enablePolling: true });

export const RealtimeProvider = ({ children }: { children: ReactNode }) => {
  const isVisible = useTabVisibility();
  return (
    <RealtimeContext.Provider value={{ enablePolling: isVisible }}>
      {children}
    </RealtimeContext.Provider>
  );
};

export const useRealtime = () => useContext(RealtimeContext);
