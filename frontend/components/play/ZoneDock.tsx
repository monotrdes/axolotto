"use client";
import type { TabId, ZoneTab } from '@/types/play';

interface ZoneDockProps {
  zoneTabs: readonly ZoneTab[];
  tabActiva: TabId;
  dailyClaimAvailable: boolean;
  onTabChange: (tab: TabId, zone: string) => void;
}

export default function ZoneDock({ zoneTabs, tabActiva, dailyClaimAvailable, onTabChange }: ZoneDockProps) {
  return (
    <nav className="fixed bottom-0 left-0 right-0 z-40 overflow-visible bg-[#060610]/90 backdrop-blur-xl border-t border-white/5">
      <div className="flex items-end justify-around px-1 pt-1 pb-2.5 max-w-xl mx-auto">

        {zoneTabs.map((tab) => {
          const isActive = tabActiva === tab.id ||
            (tab.id === 'santuario' && (tabActiva === 'criadero' || tabActiva === 'axolotitos'));
          const isSala = tab.id === 'jugar';

          return isSala ? (
            /* ── Sala: Center FAB elevated ── */
            <div key={tab.id} className="flex flex-col items-center flex-1 -translate-y-5">
              <button
                onClick={() => onTabChange('jugar', 'sala')}
                className="relative w-14 h-14 rounded-full flex items-center justify-center transition-all duration-200"
                style={
                  isActive
                    ? {
                        background: 'linear-gradient(135deg, #5EE0B0, #34D399, #059669)',
                        boxShadow: '0 0 0 3px rgba(52,211,153,0.25), 0 0 28px 4px rgba(52,211,153,0.7)',
                        transform: 'scale(1.1)',
                      }
                    : {
                        background: 'linear-gradient(135deg, #34D399, #059669)',
                        boxShadow: '0 0 0 2px rgba(52,211,153,0.15), 0 0 20px 2px rgba(52,211,153,0.4)',
                      }
                }
              >
                <span className="text-2xl leading-none select-none">{tab.emoji}</span>
              </button>
              <span
                className="text-[9px] sm:text-[10px] font-black leading-none tracking-widest mt-1.5 transition-colors duration-200 uppercase"
                style={{ color: isActive ? '#8EEDCC' : '#34D399' }}
              >
                {tab.label}
              </span>
            </div>
          ) : (
            /* ── Normal zone button ── */
            <button
              key={tab.id}
              onClick={() => onTabChange(tab.id, tab.zone)}
              className="flex flex-col items-center gap-0.5 px-1 py-0.5 rounded-xl transition-all duration-200 min-w-0 flex-1 relative"
            >
              {isActive && (
                <span
                  className="absolute -top-1.5 left-1/2 -translate-x-1/2 w-5 h-0.5 rounded-full"
                  style={{ backgroundColor: tab.color, boxShadow: `0 0 6px 2px ${tab.glow}` }}
                />
              )}
              {tab.id === 'gashapon' && dailyClaimAvailable && (
                <span className="absolute top-0 right-1.5 w-2 h-2 rounded-full bg-red-500 shadow-[0_0_6px_2px_rgba(239,68,68,0.7)] animate-pulse" />
              )}
              <span
                className="text-xl leading-none transition-all duration-200"
                style={{
                  transform: isActive ? 'scale(1.2) translateY(-1px)' : 'scale(1)',
                  filter: isActive ? `drop-shadow(0 0 6px ${tab.glow})` : 'none',
                }}
              >
                {tab.emoji}
              </span>
              <span
                className="text-[9px] sm:text-[10px] font-semibold leading-none truncate max-w-[44px] transition-colors duration-200"
                style={{ color: isActive ? tab.color : '#4B5563' }}
              >
                {tab.label}
              </span>
            </button>
          );
        })}

      </div>
    </nav>
  );
}
