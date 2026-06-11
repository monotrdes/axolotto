"use client";
import React, { useCallback, useEffect, useState } from "react";
import axios from "axios";
import { API_BASE } from "@/lib/api";
import { useToast } from "@/context/ToastContext";
import type { DecoracionesData } from "@/components/world/zones/santuario/SantuarioScene";

/**
 * Panel de decoración del mundo papel picado (plan task-84): se abre al tocar
 * un slot tipado de la sala del Santuario y cierra el loop completo —
 * slot vacío → comprar con FRJ → equipar → verlo en el diorama.
 * Habla el protocolo real: /cave/decorations[/inventory|/update] y /shop/buy.
 */

const FRJ_INTERNAL = 10_000; // FRJ_DECIMALS_BACKEND = 4

const SUBCAT_INFO: Record<string, { label: string; icon: string }> = {
  AMBIENTE: { label: "Ambiente", icon: "🌅" },
  LUZ: { label: "Iluminación", icon: "🏮" },
  MESA: { label: "Mesa", icon: "🪵" },
  MANTEL: { label: "Mantel", icon: "🎀" },
  SILLAS: { label: "Sillas", icon: "🪑" },
  FONDO: { label: "Fondo", icon: "🪷" },
  ESPECIAL: { label: "Especial", icon: "📻" },
};

const RARITY_BADGE: Record<string, string> = {
  common: "bg-gray-600/60 text-gray-200",
  rare: "bg-blue-600/60 text-blue-100",
  epic: "bg-purple-600/60 text-purple-100",
  legendary: "bg-amber-500/70 text-amber-950",
};
const RARITY_LABEL: Record<string, string> = {
  common: "Común",
  rare: "Raro",
  epic: "Épico",
  legendary: "Legendario",
};

interface InventoryItem {
  id: number;
  name: string;
  description?: string;
  rarity: string;
  quantity: number;
  item_metadata: Record<string, unknown>;
}

interface CatalogItem {
  id: number;
  name: string;
  description?: string;
  rarity: string;
  price_gal: number | null;
  user_owned?: number;
  max_per_user?: number | null;
  item_metadata: Record<string, unknown>;
}

interface DecorSlotPanelProps {
  isOpen: boolean;
  onClose: () => void;
  slotId: string | null;
  token: string | null;
  userId: string;
  /** Re-sincroniza diorama y saldos tras equipar/comprar. */
  onChanged: () => void;
}

const DecorSlotPanel: React.FC<DecorSlotPanelProps> = (props) => {
  if (!props.isOpen || !props.slotId) return null;
  return <DecorSlotPanelInner key={props.slotId} {...props} />;
};

const DecorSlotPanelInner: React.FC<DecorSlotPanelProps> = ({
  onClose,
  slotId,
  token,
  userId,
  onChanged,
}) => {
  const { toast } = useToast();
  const subcat = (slotId ?? "").split("_")[0];
  const info = SUBCAT_INFO[subcat] ?? { label: subcat, icon: "🏺" };

  const [tab, setTab] = useState<"equipar" | "comprar">("equipar");
  const [decor, setDecor] = useState<DecoracionesData | null>(null);
  const [inventario, setInventario] = useState<InventoryItem[]>([]);
  const [catalogo, setCatalogo] = useState<CatalogItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [busy, setBusy] = useState(false);

  const headers = { Authorization: `Bearer ${token}` };

  const cargar = useCallback(async () => {
    if (!token) return;
    try {
      const [decorRes, invRes, shopRes] = await Promise.all([
        axios.get(`${API_BASE}/cave/decorations`, { headers }),
        axios.get(`${API_BASE}/cave/decorations/inventory`, { headers }),
        axios.get(`${API_BASE}/shop/items`, { params: { user_id: userId } }),
      ]);
      setDecor(decorRes.data);
      setInventario(invRes.data?.items_by_category?.[subcat] ?? []);
      setCatalogo(
        (Array.isArray(shopRes.data) ? shopRes.data : []).filter(
          (i: CatalogItem & { item_type?: string }) =>
            i.item_type?.toUpperCase() === "CAVE_ITEM" &&
            i.item_metadata?.cave_subcategory === subcat,
        ),
      );
    } catch (e) {
      console.error("DecorSlotPanel: error cargando datos", e);
      toast.error("No se pudo cargar la decoración");
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [token, userId, subcat]);

  // Carga inicial: el panel se remonta por slot (key=slotId), loading parte
  // en true y se apaga cuando responde el backend (sistema externo).
  useEffect(() => {
    let active = true;
    // eslint-disable-next-line react-hooks/set-state-in-effect -- fetch inicial: el setState ocurre tras la respuesta de red, no síncrono
    cargar().finally(() => {
      if (active) setLoading(false);
    });
    return () => {
      active = false;
    };
  }, [cargar]);

  const equippedItemId = decor?.decorations?.[slotId ?? ""] ?? null;

  const actualizarSlot = async (itemId: number | null) => {
    if (!token || !slotId || busy) return;
    setBusy(true);
    try {
      const res = await axios.post(
        `${API_BASE}/cave/decorations/update`,
        { decorations: { ...(decor?.decorations ?? {}), [slotId]: itemId } },
        { headers },
      );
      setDecor(res.data);
      toast.ok(itemId === null ? "Decoración retirada" : "✨ ¡Decoración colocada!");
      onChanged();
      // Refrescar inventario (cantidades cambian al equipar/quitar)
      const invRes = await axios.get(`${API_BASE}/cave/decorations/inventory`, { headers });
      setInventario(invRes.data?.items_by_category?.[subcat] ?? []);
    } catch (e: unknown) {
      const detail = axios.isAxiosError(e) ? e.response?.data?.detail : null;
      toast.error(detail || "No se pudo actualizar la decoración");
    } finally {
      setBusy(false);
    }
  };

  const comprar = async (item: CatalogItem) => {
    if (!token || busy) return;
    setBusy(true);
    try {
      await axios.post(
        `${API_BASE}/shop/buy`,
        { user_id: userId, item_id: item.id, payment_currency: "frijolito" },
        { headers },
      );
      toast.ok(`🛒 ¡${item.name} comprado!`);
      onChanged(); // refresca saldos
      await cargar();
      setTab("equipar");
    } catch (e: unknown) {
      const detail = axios.isAxiosError(e) ? e.response?.data?.detail : null;
      toast.error(detail || "No se pudo comprar");
    } finally {
      setBusy(false);
    }
  };

  const precioFrj = (raw: number | null) => Math.round((raw ?? 0) / FRJ_INTERNAL);

  return (
    <div
      className="fixed inset-0 z-[120] flex items-end justify-center bg-black/60 backdrop-blur-sm"
      onClick={onClose}
    >
      <div
        className="bg-[#12122A] border border-[#E4007C]/20 rounded-t-2xl w-full max-w-md max-h-[72vh] overflow-y-auto p-5 animate-slide-up"
        onClick={(e) => e.stopPropagation()}
      >
        {/* Header */}
        <div className="flex items-center justify-between mb-1">
          <h3 className="text-white font-bold text-lg">
            {info.icon} {info.label}
          </h3>
          <button
            onClick={onClose}
            className="text-gray-400 hover:text-white text-xl leading-none"
          >
            ✕
          </button>
        </div>
        <p className="text-gray-500 text-xs mb-3">
          Slot <span className="text-[#FF8DA1] font-bold">{slotId}</span> de tu cueva
        </p>

        {/* Tabs */}
        <div className="flex gap-1.5 mb-3">
          {(
            [
              { id: "equipar", label: "🎒 Equipar" },
              { id: "comprar", label: "🛒 Comprar" },
            ] as const
          ).map((t) => (
            <button
              key={t.id}
              onClick={() => setTab(t.id)}
              className={`flex-1 py-1.5 rounded-lg text-xs font-bold transition-all ${
                tab === t.id
                  ? "bg-[#E4007C]/25 text-[#FF8DA1] border border-[#E4007C]/40"
                  : "bg-[#1C1C35] text-gray-500 border border-white/5 hover:text-gray-300"
              }`}
            >
              {t.label}
            </button>
          ))}
        </div>

        {loading ? (
          <p className="text-center text-gray-500 text-sm py-8 animate-pulse">
            🪸 Cargando…
          </p>
        ) : tab === "equipar" ? (
          <>
            {equippedItemId !== null && (
              <button
                onClick={() => actualizarSlot(null)}
                disabled={busy}
                className="w-full mb-3 py-2 rounded-xl bg-[#1C1C35] border border-white/10 text-gray-300 text-xs font-bold hover:border-red-500/40 hover:text-red-300 transition-all disabled:opacity-50"
              >
                Quitar {decor?.items?.[String(equippedItemId)]?.emoji ?? ""}{" "}
                {decor?.items?.[String(equippedItemId)]?.name ?? "lo equipado"}
              </button>
            )}
            {inventario.length === 0 ? (
              <div className="text-center py-6">
                <span className="text-3xl">🎒</span>
                <p className="text-gray-500 text-sm mt-1">
                  No tienes decoraciones de {info.label.toLowerCase()}.
                </p>
                <button
                  onClick={() => setTab("comprar")}
                  className="mt-2 px-4 py-1.5 rounded-full bg-[#E4007C] text-white text-xs font-bold hover:bg-[#ff1a8c]"
                >
                  Ver el catálogo →
                </button>
              </div>
            ) : (
              <div className="grid grid-cols-3 gap-2">
                {inventario.map((item) => (
                  <button
                    key={item.id}
                    onClick={() => actualizarSlot(item.id)}
                    disabled={busy || item.id === equippedItemId}
                    className={`flex flex-col items-center rounded-xl p-2 border transition-all ${
                      item.id === equippedItemId
                        ? "bg-[#E4007C]/20 border-[#E4007C]/60"
                        : "bg-[#1C1C35] border-white/5 hover:border-white/20 active:scale-95"
                    }`}
                  >
                    <span className="text-2xl">
                      {(item.item_metadata?.emoji as string) || "🏺"}
                    </span>
                    <span className="text-[10px] font-bold text-white mt-0.5 text-center leading-tight line-clamp-2">
                      {item.name}
                    </span>
                    <span
                      className={`mt-1 px-1.5 rounded-full text-[8px] font-black uppercase ${RARITY_BADGE[item.rarity] ?? RARITY_BADGE.common}`}
                    >
                      {RARITY_LABEL[item.rarity] ?? item.rarity}
                    </span>
                    {item.id === equippedItemId && (
                      <span className="text-[9px] text-[#FF8DA1] font-bold mt-0.5">
                        Equipado ✓
                      </span>
                    )}
                  </button>
                ))}
              </div>
            )}
          </>
        ) : (
          <>
            {catalogo.length === 0 ? (
              <p className="text-center text-gray-500 text-sm py-6">
                Aún no hay {info.label.toLowerCase()} en el catálogo.
              </p>
            ) : (
              <div className="space-y-2">
                {catalogo.map((item) => {
                  const agotado =
                    item.max_per_user != null &&
                    (item.user_owned ?? 0) >= item.max_per_user;
                  return (
                    <div
                      key={item.id}
                      className="flex items-center gap-3 bg-[#1C1C35] border border-white/5 rounded-xl p-2.5"
                    >
                      <span className="text-2xl">
                        {(item.item_metadata?.emoji as string) || "🏺"}
                      </span>
                      <div className="flex-1 min-w-0">
                        <div className="flex items-center gap-1.5">
                          <span className="text-xs font-bold text-white truncate">
                            {item.name}
                          </span>
                          <span
                            className={`px-1.5 rounded-full text-[8px] font-black uppercase shrink-0 ${RARITY_BADGE[item.rarity] ?? RARITY_BADGE.common}`}
                          >
                            {RARITY_LABEL[item.rarity] ?? item.rarity}
                          </span>
                        </div>
                        {item.description && (
                          <p className="text-[10px] text-gray-500 truncate">
                            {item.description}
                          </p>
                        )}
                      </div>
                      <button
                        onClick={() => comprar(item)}
                        disabled={busy || agotado}
                        className="shrink-0 px-3 py-1.5 rounded-lg bg-amber-600/80 hover:bg-amber-500 text-white text-[11px] font-black transition-all disabled:opacity-40 disabled:cursor-not-allowed"
                      >
                        {agotado ? "Agotado" : `🪙 ${precioFrj(item.price_gal)} FRJ`}
                      </button>
                    </div>
                  );
                })}
              </div>
            )}
          </>
        )}

        {/* Bonos activos */}
        {decor && "bonuses" in decor && (
          <div className="mt-4 pt-3 border-t border-white/5 flex justify-around text-center">
            {(() => {
              const b = (decor as unknown as {
                bonuses?: Record<string, number>;
              }).bonuses;
              if (!b) return null;
              return (
                <>
                  <div>
                    <p className="text-[9px] text-gray-500 font-bold uppercase">🔋 Focus</p>
                    <p className="text-xs font-black text-emerald-400">
                      +{Math.round((b.focus_recovery_boost ?? 0) * 100)}%
                    </p>
                  </div>
                  <div>
                    <p className="text-[9px] text-gray-500 font-bold uppercase">💰 Staking</p>
                    <p className="text-xs font-black text-amber-400">
                      +{Math.round((b.frj_staking_multiplier ?? 0) * 100)}%
                    </p>
                  </div>
                  <div>
                    <p className="text-[9px] text-gray-500 font-bold uppercase">🥚 Incubación</p>
                    <p className="text-xs font-black text-sky-400">
                      +{Math.round((b.incubation_boost_total ?? 0) * 100)}%
                    </p>
                  </div>
                </>
              );
            })()}
          </div>
        )}
      </div>
    </div>
  );
};

export { DecorSlotPanel };
export default DecorSlotPanel;
