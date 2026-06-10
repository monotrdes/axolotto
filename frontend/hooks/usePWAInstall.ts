import { useState, useEffect } from 'react';

export function usePWAInstall() {
  const [deferredPrompt, setDeferredPrompt] = useState<any>(null);
  const [isInstallable, setIsInstallable] = useState(false);
  const [isStandalone, setIsStandalone] = useState(false);
  const [isIOS, setIsIOS] = useState(false);
  const [showInstallPrompt, setShowInstallPrompt] = useState(false);

  useEffect(() => {
    if (typeof window === 'undefined') return;

    // Check if running in standalone mode (installed as PWA)
    const checkStandalone = () => {
      const isStandaloneMedia = window.matchMedia('(display-mode: standalone)').matches;
      const isIOSStandalone = (window.navigator as any).standalone === true;
      return isStandaloneMedia || isIOSStandalone;
    };

    // Check if device is iOS
    const checkIOS = () => {
      return /iPad|iPhone|iPod/.test(navigator.userAgent) && !(window as any).MSStream;
    };

    const standalone = checkStandalone();
    const ios = checkIOS();

    setIsStandalone(standalone);
    setIsIOS(ios);

    // If already standalone, we don't need any install prompting
    if (standalone) return;

    // Listen to the native beforeinstallprompt event (Android / Desktop Chrome / etc.)
    const handleBeforeInstallPrompt = (e: Event) => {
      e.preventDefault();
      setDeferredPrompt(e);
      setIsInstallable(true);

      // Show toast/banner automatically if they haven't dismissed it in the last 7 days
      const dismissedTime = localStorage.getItem('pwa_prompt_dismissed_time');
      const oneWeek = 7 * 24 * 60 * 60 * 1000;
      const recentlyDismissed = dismissedTime && (Date.now() - parseInt(dismissedTime, 10) < oneWeek);

      if (!recentlyDismissed) {
        // Show after a short delay to not overwhelm the user
        const timer = setTimeout(() => {
          setShowInstallPrompt(true);
        }, 3000);
        return () => clearTimeout(timer);
      }
    };

    window.addEventListener('beforeinstallprompt', handleBeforeInstallPrompt);

    // For iOS, since beforeinstallprompt doesn't fire, we can prompt them manually
    // if they haven't dismissed it recently
    if (ios) {
      const dismissedTime = localStorage.getItem('pwa_prompt_dismissed_time');
      const oneWeek = 7 * 24 * 60 * 60 * 1000;
      const recentlyDismissed = dismissedTime && (Date.now() - parseInt(dismissedTime, 10) < oneWeek);

      if (!recentlyDismissed) {
        const timer = setTimeout(() => {
          setShowInstallPrompt(true);
        }, 5000);
        return () => clearTimeout(timer);
      }
    }

    return () => {
      window.removeEventListener('beforeinstallprompt', handleBeforeInstallPrompt);
    };
  }, []);

  const installApp = async (): Promise<boolean> => {
    if (!deferredPrompt) return false;

    // Show the browser's install dialog
    deferredPrompt.prompt();

    // Wait for the user's response
    const { outcome } = await deferredPrompt.userChoice;
    if (outcome === 'accepted') {
      setDeferredPrompt(null);
      setIsInstallable(false);
      setShowInstallPrompt(false);
      return true;
    }
    return false;
  };

  const dismissPrompt = () => {
    setShowInstallPrompt(false);
    // Save dismiss timestamp to avoid prompting again too soon
    localStorage.setItem('pwa_prompt_dismissed_time', Date.now().toString());
  };

  const forceShowPrompt = () => {
    setShowInstallPrompt(true);
  };

  return {
    isInstallable: isInstallable || isIOS, // either native beforeinstallprompt OR iOS manual flow
    isStandalone,
    isIOS,
    showInstallPrompt,
    installApp,
    dismissPrompt,
    forceShowPrompt
  };
}
