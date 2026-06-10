type NavTab = 'santuario' | 'jugar' | 'mercado' | 'amigos' | 'perfil';

interface Amigo {
  id: string;
  name: string;
  avatarEmoji?: string;
}

interface ZonaInferiorProps {
  amigos?: Amigo[];
  activeTab?: NavTab;
  onNavigate?: (tab: NavTab) => void;
  onLike?: (amigoId: string) => void;
  onInvite?: (amigoId: string) => void;
  onVisit?: (amigoId: string) => void;
}

const NAV_ITEMS: { tab: NavTab; icon: string; label: string }[] = [
  { tab: 'santuario', icon: '🦎', label: 'Santuario' },
  { tab: 'jugar',     icon: '🎲', label: 'Jugar'     },
  { tab: 'mercado',   icon: '🛒', label: 'Mercado'   },
  { tab: 'amigos',    icon: '👥', label: 'Amigos'    },
  { tab: 'perfil',    icon: '👤', label: 'Perfil'    },
];

export default function ZonaInferior({
  amigos = [],
  activeTab = 'santuario',
  onNavigate,
  onLike,
  onInvite,
  onVisit,
}: ZonaInferiorProps) {
  const visible = amigos.slice(0, 4);

  return (
    <div className="flex flex-col border-t border-slate-700/60 bg-slate-900/95 shrink-0">
      {/* Friends list */}
      <div className="py-1">
        {visible.length === 0 ? (
          <p className="text-center text-[10px] text-slate-500 py-2">Sin amigos activos</p>
        ) : (
          visible.map((amigo) => (
            <div key={amigo.id} className="flex items-center gap-2 px-3 py-1.5">
              {/* Avatar */}
              <div className="w-7 h-7 rounded-full bg-teal-800 flex items-center justify-center text-xs shrink-0">
                {amigo.avatarEmoji ?? amigo.name.charAt(0).toUpperCase()}
              </div>
              {/* Name */}
              <span className="flex-1 text-xs font-bold text-white truncate">{amigo.name}</span>
              {/* Action buttons */}
              <button
                onClick={() => onLike?.(amigo.id)}
                className="text-[9px] px-2 py-0.5 rounded-full bg-pink-900/50 border border-pink-500/30 text-pink-300"
              >
                ❤️ Like
              </button>
              <button
                onClick={() => onInvite?.(amigo.id)}
                className="text-[9px] px-2 py-0.5 rounded-full bg-teal-900/50 border border-teal-500/30 text-teal-300"
              >
                ➕ Invitar
              </button>
              <button
                onClick={() => onVisit?.(amigo.id)}
                className="text-[9px] px-2 py-0.5 rounded-full bg-slate-800 border border-white/10 text-slate-300"
              >
                👁 Visitar
              </button>
            </div>
          ))
        )}
      </div>

      {/* Nav bar */}
      <div className="flex items-center border-t border-slate-700/60">
        {NAV_ITEMS.map(({ tab, icon, label }) => {
          const isActive = tab === activeTab;
          return (
            <button
              key={tab}
              onClick={() => onNavigate?.(tab)}
              className={`flex-1 flex flex-col items-center py-2 gap-0.5 ${isActive ? 'text-white' : 'text-slate-500'}`}
            >
              <span className="text-base leading-none">{icon}</span>
              <span className="text-[9px] leading-none">{label}</span>
              {isActive && <span className="w-4 h-0.5 rounded-full bg-teal-400 mt-0.5" />}
            </button>
          );
        })}
      </div>
    </div>
  );
}
