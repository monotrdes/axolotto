"use client";
import type { VipTier, VipPresentation } from "@/lib/vip";
import { VIP_PRESENTATION } from "@/lib/vip";
import TierCard from "./TierCard";

interface ModeAProps {
  tiers: VipTier[];
  tiersLoading: boolean;
  tiersError: boolean;
  onRetry: () => void;
  selectedTierId: string;
  setSelectedTierId: (id: string) => void;
  activeVipCount: number | null;
  balances: Record<string, number> | null;
  purchasing: boolean;
  onPurchase: (tierId: string) => void;
}

/**
 * Modo A — Ventas: muestra el catalogo de planes VIP con segmented control.
 */
export default function ModeA({
  tiers,
  tiersLoading,
  tiersError,
  onRetry,
  selectedTierId,
  setSelectedTierId,
  activeVipCount,
  balances,
  purchasing,
  onPurchase,
}: ModeAProps) {
  // ── Loading state ──
  if (tiersLoading) {
    return (
      <div className="space-y-4">
        <div className="text-center py-2">
          <div className="text-3xl mb-2">👑</div>
          <div className="h-6 bg-white/10 rounded-lg w-3/4 mx-auto mb-2 animate-pulse" />
          <div className="h-4 bg-white/5 rounded-lg w-1/2 mx-auto animate-pulse" />
        </div>
        <TierSkeleton />
      </div>
    );
  }

  // ── Error state ──
  if (tiersError) {
    return (
      <div className="py-8 text-center space-y-3">
        <div className="text-4xl">⚠️</div>
        <p className="text-sm text-gray-400">
          No se pudieron cargar los planes VIP.
        </p>
        <button
          onClick={onRetry}
          className="px-5 py-2.5 rounded-xl bg-white/10 hover:bg-white/20 text-white text-sm font-bold transition-all min-h-[44px]"
        >
          Reintentar
        </button>
      </div>
    );
  }

  const selectedTier = tiers.find((t) => t.id === selectedTierId) ?? null;
  const selectedPres = selectedTier ? VIP_PRESENTATION[selectedTier.id] : null;

  return (
    <>
      {/* Hook de valor */}
      <div className="text-center py-2">
        <div className="text-3xl mb-2">👑</div>
        <h2 className="text-lg font-black text-white leading-tight">
          El club se paga solo.
        </h2>
        <p className="text-xs text-gray-400 mt-1 max-w-xs mx-auto">
          Recuperas mas FRJ de los que inviertes cada mes. Cada plan incluye
          Frijolitos diarios, descuentos y Gashapones.
        </p>
      </div>

      {/* Prueba social */}
      {activeVipCount !== null && (
        <div className="text-center">
          <span className="text-xs font-bold text-amber-400 bg-amber-400/10 px-3 py-1.5 rounded-full border border-amber-400/20">
            🔥 {activeVipCount.toLocaleString("es-MX")} VIP activos ahora
          </span>
        </div>
      )}

      {/* Tease del marco cosmetico */}
      {selectedTierId && selectedPres && (
        <div className="flex flex-col items-center gap-2">
          <div className="relative w-16 h-16">
            <div
              className={`absolute inset-0 pointer-events-none vip-frame-${selectedTierId}`}
            />
            <div
              className="w-full h-full rounded-full flex items-center justify-center text-2xl animate-axo-bob"
              style={{
                background: selectedPres
                  ? `radial-gradient(circle, ${selectedPres.color}22, transparent)`
                  : "rgba(255,255,255,0.05)",
              }}
            >
              {selectedPres?.emoji ?? "🦎"}
            </div>
          </div>
          <p className="text-xs text-gray-500 font-medium">
            Tu Axolotito lleva el marco de tu rango
          </p>
        </div>
      )}

      {/* Segmented control de tiers */}
      {tiers.length > 0 && (
        <div
          className="flex rounded-xl overflow-hidden border border-white/10 bg-white/5"
          role="tablist"
          aria-label="Seleccionar nivel VIP"
        >
          {tiers.map((t) => {
            const pres = VIP_PRESENTATION[t.id];
            const isActive = t.id === selectedTierId;
            if (!pres) return null;
            return (
              <button
                key={t.id}
                role="tab"
                aria-selected={isActive}
                onClick={() => setSelectedTierId(t.id)}
                className="flex-1 py-3 font-black text-xs transition-all relative min-h-[44px]"
                style={{
                  color: isActive ? pres.color ?? "#fff" : "#6B7280",
                  background: isActive
                    ? (pres.color ?? "#fff") + "15"
                    : "transparent",
                  borderBottom: isActive
                    ? `2px solid ${pres.color ?? "#fff"}`
                    : "2px solid transparent",
                }}
              >
                <span className="mr-1">{pres.emoji}</span>
                {pres.label}
                {t.popular && (
                  <span
                    className="absolute -top-1.5 right-1 text-[8px] font-black px-1 py-0.5 rounded-full"
                    style={{ background: "#FBBF24", color: "#0A0A1A" }}
                  >
                    ★
                  </span>
                )}
              </button>
            );
          })}
        </div>
      )}

      {/* Tarjeta del tier seleccionado */}
      {selectedTier && selectedPres ? (
        <TierCard
          tier={selectedTier}
          balances={balances}
          purchasing={purchasing}
          onPurchase={onPurchase}
        />
      ) : (
        !tiersLoading && !tiersError && tiers.length === 0 && (
          <p className="text-sm text-gray-500 text-center py-6">
            No hay planes disponibles en este momento.
          </p>
        )
      )}

      {/* Teaser de recompensas */}
      <div className="rounded-xl px-4 py-3 text-center border border-white/10 bg-white/5">
        <p className="text-xs text-gray-400 font-bold">
          Mantente activo y desbloquea marcos exclusivos
        </p>
        <p className="text-xs text-gray-600 mt-1">
          Hitos en 3, 6, 12 y 24 meses de racha consecutiva
        </p>
      </div>

      {/* Nota legal */}
      <p className="text-center text-xs text-gray-600 pb-1">
        Los dias se apilan si renuevas antes de vencer. Los slots extra se
        congelan (no se pierden) si expira la membresia.
      </p>
    </>
  );
}

/** Skeleton de carga para las tarjetas de tier */
function TierSkeleton() {
  return (
    <div className="animate-pulse space-y-3">
      <div className="h-9 bg-white/10 rounded-xl" />
      <div className="h-48 bg-white/5 rounded-2xl" />
      <div className="h-12 bg-white/10 rounded-xl" />
    </div>
  );
}
