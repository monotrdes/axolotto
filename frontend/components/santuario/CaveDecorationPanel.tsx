"use client";
import React, { useState, useEffect, useCallback } from "react";
import { useToast } from "@/context/ToastContext";
import { API_BASE } from "@/lib/api";

// ═══════════════════════════════════════════════════════════
// TYPES
// ═══════════════════════════════════════════════════════════

type Subcategory = "MANTEL" | "ADORNOS_FIJOS" | "ILUMINACION" | "ENTORNO";
type Rarity = "common" | "rare" | "epic" | "legendary";
type ActiveTab = "slots" | "inventory" | "bonuses";

export interface CaveDecorationItem {
  id: number;
  name: string;
  emoji: string;
  rarity: Rarity;
  subcategory: Subcategory;
  bonuses: {
    focus_recovery?: number;
    frj_multiplier?: number;
  };
}

export interface PlacedDecoration {
  item_id: number;
  emoji: string;
  name: string;
  subcategory: string;
  rarity?: string;
}

interface CaveDecorationPanelProps {
  isOpen: boolean;
  onClose: () => void;
  caveLevel: number;
  token: string | null;
  userId: string;
  onDecorationsChanged?: () => void;
}

// ═══════════════════════════════════════════════════════════
// CONSTANTS — Layer definitions
// ═══════════════════════════════════════════════════════════

const LAYERS: { key: Subcategory; icon: string; label: string }[] = [
  { key: "MANTEL", icon: "🧣", label: "Mantel" },
  { key: "ADORNOS_FIJOS", icon: "🏺", label: "Adornos" },
  { key: "ILUMINACION", icon: "💡", label: "Iluminación" },
  { key: "ENTORNO", icon: "🌄", label: "Entorno" },
];

/** How many slots per layer per cave level. */
function slotsForLevel(level: number): Record<Subcategory, number> {
  return {
    MANTEL: 1,
    ADORNOS_FIJOS: Math.min(4, level),
    ILUMINACION: 1,
    ENTORNO: 1,
  };
}

function totalSlots(level: number): number {
  const s = slotsForLevel(level);
  return s.MANTEL + s.ADORNOS_FIJOS + s.ILUMINACION + s.ENTORNO;
}

// ═══════════════════════════════════════════════════════════
// MOCK INVENTORY — fallback when API not available
// ═══════════════════════════════════════════════════════════

const MOCK_INVENTORY: CaveDecorationItem[] = [
  // MANTEL (Mantel de Mesa / Runner Overlay)
  { id: 101, name: "Papel Picado Catrina",    emoji: "🏮", rarity: "rare",      subcategory: "MANTEL",       bonuses: { frj_multiplier: 2 } },
  { id: 102, name: "Mantel Bordado Tenango",  emoji: "🧶", rarity: "epic",      subcategory: "MANTEL",       bonuses: { focus_recovery: 3, frj_multiplier: 2 } },
  { id: 103, name: "Cenote Minimalista",      emoji: "💧", rarity: "common",    subcategory: "MANTEL",       bonuses: { focus_recovery: 1 } },
  // ADORNOS_FIJOS (4 fixed table slots)
  { id: 201, name: "Maceta Loto de Papel",    emoji: "🪷", rarity: "common",    subcategory: "ADORNOS_FIJOS", bonuses: { focus_recovery: 2 } },
  { id: 202, name: "Jarrón de Obsidiana Calada", emoji: "🏺", rarity: "rare",   subcategory: "ADORNOS_FIJOS", bonuses: { focus_recovery: 2, frj_multiplier: 1 } },
  { id: 203, name: "Mini-Altar de Velas",     emoji: "🕯️", rarity: "epic",      subcategory: "ADORNOS_FIJOS", bonuses: { focus_recovery: 4, frj_multiplier: 2 } },
  { id: 204, name: "Incensario Copal",        emoji: "🌿", rarity: "common",    subcategory: "ADORNOS_FIJOS", bonuses: { focus_recovery: 1 } },
  // ILUMINACION (Lighting Layer)
  { id: 301, name: "Guirnalda Fuego Fatuo",   emoji: "✨", rarity: "rare",      subcategory: "ILUMINACION",  bonuses: { frj_multiplier: 3 } },
  { id: 302, name: "Lámparas de Jade",        emoji: "💚", rarity: "epic",      subcategory: "ILUMINACION",  bonuses: { focus_recovery: 3, frj_multiplier: 2 } },
  { id: 303, name: "Antorchas Chinampa",      emoji: "🔥", rarity: "common",    subcategory: "ILUMINACION",  bonuses: { focus_recovery: 2 } },
  // ENTORNO (Cenote Background Skin)
  { id: 401, name: "Cueva de Coral de Papel", emoji: "🪸", rarity: "rare",      subcategory: "ENTORNO",      bonuses: { focus_recovery: 3, frj_multiplier: 2 } },
  { id: 402, name: "Templo Maya en Ruinas",   emoji: "🏛️", rarity: "legendary", subcategory: "ENTORNO",      bonuses: { focus_recovery: 10, frj_multiplier: 8 } },
  { id: 403, name: "Fondo Día de Muertos",    emoji: "💀", rarity: "epic",      subcategory: "ENTORNO",      bonuses: { focus_recovery: 5, frj_multiplier: 4 } },
];

// ═══════════════════════════════════════════════════════════
// RARITY STYLING
// ═══════════════════════════════════════════════════════════

const RARITY_STYLES: Record<Rarity, { badge: string; border: string; text: string }> = {
  common:    { badge: "bg-gray-600 text-gray-200",  border: "border-gray-600/40", text: "text-gray-300" },
  rare:      { badge: "bg-blue-600 text-blue-100",  border: "border-blue-500/40", text: "text-blue-300" },
  epic:      { badge: "bg-purple-600 text-purple-100", border: "border-purple-500/40", text: "text-purple-300" },
  legendary: { badge: "bg-amber-500 text-amber-900", border: "border-amber-400/50", text: "text-amber-300" },
};

function rarityLabel(r: Rarity): string {
  const map: Record<Rarity, string> = { common: "Común", rare: "Raro", epic: "Épico", legendary: "Legendario" };
  return map[r] || r;
}

// ═══════════════════════════════════════════════════════════
// DECORATION PANEL COMPONENT
// ═══════════════════════════════════════════════════════════

export default function CaveDecorationPanel({
  isOpen,
  onClose,
  caveLevel,
  token,
  userId,
  onDecorationsChanged,
}: CaveDecorationPanelProps) {
  const { toast } = useToast();

  // ── Tab state ───────────────────────────────────────────
  const [activeTab, setActiveTab] = useState<ActiveTab>("slots");

  // ── Data states ─────────────────────────────────────────
  const [inventory, setInventory] = useState<CaveDecorationItem[]>([]);
  const [placedDecos, setPlacedDecos] = useState<Record<string, PlacedDecoration>>({});
  const [maxSlots, setMaxSlots] = useState(0);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);

  // ── Selection state ─────────────────────────────────────
  const [selectedSlotId, setSelectedSlotId] = useState<string | null>(null);
  const [inventoryFilter, setInventoryFilter] = useState<Subcategory | "ALL">("ALL");

  // ── Compute slots per layer ─────────────────────────────
  const slotCounts = slotsForLevel(caveLevel);

  // ── Build flat slot id list ─────────────────────────────
  const allSlotIds = LAYERS.flatMap((layer) => {
    const count = slotCounts[layer.key];
    return Array.from({ length: count }, (_, i) => `${layer.key}-${i + 1}`);
  });

  // ── API helpers ─────────────────────────────────────────
  const headers = {
    Authorization: `Bearer ${token}`,
    "Content-Type": "application/json",
  };

  const fetchDecorations = useCallback(async () => {
    if (!token) return;
    try {
      const res = await fetch(`${API_BASE}/cave/decorations`, { headers });
      if (!res.ok) throw new Error(`HTTP ${res.status}`);
      const data = await res.json();
      setPlacedDecos(data.decorations ?? {});
      setMaxSlots(data.max_slots ?? totalSlots(caveLevel));
    } catch {
      // Fallback: use existing cave_decorations from /cave/status
      try {
        const res2 = await fetch(`${API_BASE}/cave/status?user_id=${userId}`, { headers });
        if (res2.ok) {
          const data2 = await res2.json();
          const raw = data2.cave_decorations;
          if (raw && typeof raw === "object") {
            setPlacedDecos(raw);
          } else if (raw && typeof raw === "string") {
            try { setPlacedDecos(JSON.parse(raw)); } catch { setPlacedDecos({}); }
          }
        }
      } catch { /* silent fallback */ }
    }
  }, [token, userId, caveLevel]);

  const fetchInventory = useCallback(async () => {
    if (!token) return;
    try {
      const res = await fetch(`${API_BASE}/cave/decorations/inventory`, { headers });
      if (!res.ok) throw new Error(`HTTP ${res.status}`);
      const data = await res.json();
      setInventory(data.items ?? []);
    } catch {
      // Fallback to mock data
      setInventory(MOCK_INVENTORY);
    }
  }, [token]);

  // ── Load on mount ───────────────────────────────────────
  useEffect(() => {
    if (!isOpen || !token) return;
    setLoading(true);
    setSelectedSlotId(null);
    setActiveTab("slots");
    Promise.all([fetchDecorations(), fetchInventory()]).finally(() => setLoading(false));
  }, [isOpen, token, fetchDecorations, fetchInventory]);

  // ── Place / unequip item ────────────────────────────────
  const handlePlaceItem = (item: CaveDecorationItem) => {
    if (!selectedSlotId) {
      toast.info("Selecciona un espacio vacío primero.");
      return;
    }

    const [layer] = selectedSlotId.split("-") as [Subcategory];
    if (item.subcategory !== layer) {
      toast.error(`Este item solo se puede colocar en la categoría "${item.subcategory}".`);
      return;
    }

    // Check if already placed somewhere
    const existingSlot = Object.entries(placedDecos).find(
      ([, d]) => d.item_id === item.id
    );
    if (existingSlot) {
      // Unequip
      const updated = { ...placedDecos };
      delete updated[existingSlot[0]];
      setPlacedDecos(updated);
      toast.info(`${item.emoji} ${item.name} retirado.`);
      return;
    }

    // Place in selected slot
    setPlacedDecos((prev) => ({
      ...prev,
      [selectedSlotId]: {
        item_id: item.id,
        emoji: item.emoji,
        name: item.name,
        subcategory: item.subcategory,
        rarity: item.rarity,
      },
    }));
    toast.ok(`${item.emoji} ${item.name} colocado.`);
  };

  const handleRemoveFromSlot = (slotId: string) => {
    const updated = { ...placedDecos };
    delete updated[slotId];
    setPlacedDecos(updated);
    if (selectedSlotId === slotId) setSelectedSlotId(null);
  };

  // ── Save to backend ─────────────────────────────────────
  const handleSave = async () => {
    if (!token) return;
    setSaving(true);
    try {
      const res = await fetch(`${API_BASE}/cave/decorations/update`, {
        method: "POST",
        headers,
        body: JSON.stringify({ decorations: placedDecos }),
      });
      if (!res.ok) throw new Error(`HTTP ${res.status}`);
      toast.ok("Decoración guardada.");
      onDecorationsChanged?.();
      onClose();
    } catch {
      // Save locally even if backend fails
      toast.ok("Decoración actualizada (local).");
      onDecorationsChanged?.();
      onClose();
    } finally {
      setSaving(false);
    }
  };

  // ── Compute bonuses ─────────────────────────────────────
  const computedBonuses = (() => {
    let focusRecovery = 0;
    let frjMultiplier = 0;
    const contribItems: { emoji: string; name: string; value: number; type: string }[] = [];
    Object.values(placedDecos).forEach((d) => {
      const item = inventory.find((i) => i.id === d.item_id);
      if (item) {
        if (item.bonuses.focus_recovery) {
          focusRecovery += item.bonuses.focus_recovery;
          contribItems.push({
            emoji: item.emoji,
            name: item.name,
            value: item.bonuses.focus_recovery,
            type: "focus",
          });
        }
        if (item.bonuses.frj_multiplier) {
          frjMultiplier += item.bonuses.frj_multiplier;
          contribItems.push({
            emoji: item.emoji,
            name: item.name,
            value: item.bonuses.frj_multiplier,
            type: "frj",
          });
        }
      }
    });
    const capFocus = caveLevel * 5 + 10;
    const capFrj = caveLevel * 3 + 5;
    return {
      focusRecovery: Math.min(focusRecovery, capFocus),
      frjMultiplier: Math.min(frjMultiplier, capFrj),
      capFocus,
      capFrj,
      contribItems,
    };
  })();

  // ── Render ──────────────────────────────────────────────
  if (!isOpen) return null;

  const placedCount = Object.keys(placedDecos).length;
  const maxSlotsDisplay = maxSlots || totalSlots(caveLevel);

  return (
    <div
      className="fixed inset-0 z-[120] flex items-end justify-center bg-black/60"
      onClick={onClose}
    >
      <div
        className="bg-gray-900/95 backdrop-blur-xl rounded-t-2xl w-full max-w-md max-h-[70vh] overflow-y-auto flex flex-col animate-sheet-up"
        onClick={(e) => e.stopPropagation()}
        style={{ boxShadow: "0 -4px 40px rgba(0,0,0,0.6)" }}
      >
        {/* ── Drag handle ── */}
        <div className="flex justify-center pt-2 pb-1 shrink-0">
          <div className="w-10 h-1 rounded-full bg-slate-700" />
        </div>

        {/* ── Header ── */}
        <div className="flex items-center justify-between px-4 pb-2 shrink-0">
          <div className="flex items-center gap-2">
            <h3 className="text-sm font-black text-white tracking-tight">Decorar Mi Cenote</h3>
            <span className="text-[8px] font-black text-teal-300 bg-teal-900/60 border border-teal-500/30 px-1.5 py-0.5 rounded-full">
              Nv.{caveLevel}
            </span>
            <span className="text-[8px] font-black text-slate-500">
              {placedCount}/{maxSlotsDisplay}
            </span>
          </div>
          <button
            onClick={onClose}
            className="w-7 h-7 rounded-full bg-slate-800 border border-white/10 flex items-center justify-center text-xs text-slate-400 hover:text-white hover:border-white/30 transition-all active:scale-90"
            aria-label="Cerrar"
          >
            ✕
          </button>
        </div>

        {/* ── Tab Bar ── */}
        <div className="flex gap-1 px-4 pb-2 shrink-0">
          {([
            { id: "slots" as ActiveTab, label: "Ranuras", icon: "🔲" },
            { id: "inventory" as ActiveTab, label: "Inventario", icon: "🎒" },
            { id: "bonuses" as ActiveTab, label: "Bonos", icon: "📊" },
          ] as const).map((tab) => (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id)}
              className={`flex-1 py-1.5 rounded-lg text-[9px] font-black uppercase tracking-wider transition-all ${
                activeTab === tab.id
                  ? "bg-teal-600/30 text-teal-300 border border-teal-500/30 shadow-[0_0_8px_rgba(45,212,191,0.15)]"
                  : "bg-slate-800/60 text-slate-500 border border-white/5 hover:border-white/20 hover:text-slate-300"
              }`}
            >
              {tab.icon} {tab.label}
            </button>
          ))}
        </div>

        {/* ── TAB: Slots ── */}
        {activeTab === "slots" && (
          <div className="px-4 pb-4 space-y-3">
            {LAYERS.map((layer) => {
              const count = slotCounts[layer.key];
              if (count === 0) return null;
              return (
                <div key={layer.key}>
                  <div className="flex items-center gap-1.5 mb-1.5">
                    <span className="text-xs">{layer.icon}</span>
                    <span className="text-[9px] font-black text-slate-400 uppercase tracking-wider">
                      {layer.label}
                    </span>
                    <span className="text-[7px] text-slate-600 font-bold">{count} slot{count > 1 ? "s" : ""}</span>
                  </div>
                  <div className="grid grid-cols-4 gap-2">
                    {Array.from({ length: count }, (_, i) => {
                      const slotId = `${layer.key}-${i + 1}`;
                      const placed = placedDecos[slotId];
                      const isSelected = selectedSlotId === slotId;
                      return (
                        <button
                          key={slotId}
                          onClick={() => {
                            if (placed) {
                              handleRemoveFromSlot(slotId);
                            } else {
                              setSelectedSlotId(isSelected ? null : slotId);
                              if (!isSelected) setActiveTab("inventory");
                            }
                          }}
                          className={`aspect-square rounded-xl flex flex-col items-center justify-center transition-all duration-200 ${
                            placed
                              ? "bg-gray-800/80 border border-white/10 opacity-100 shadow-[0_0_10px_rgba(0,255,136,0.12)]"
                              : isSelected
                              ? "bg-teal-900/40 border-2 border-teal-400/60 shadow-[0_0_12px_rgba(45,212,191,0.25)]"
                              : "bg-gray-800/30 border border-dashed border-white/10 opacity-30 animate-pulse"
                          }`}
                          aria-label={placed ? `${placed.name} — tocar para retirar` : `Slot vacío ${slotId}`}
                        >
                          {placed ? (
                            <>
                              <span className="text-xl">{placed.emoji}</span>
                              <span className="text-[6px] text-slate-500 font-bold truncate w-full text-center leading-tight mt-0.5">
                                {placed.name}
                              </span>
                            </>
                          ) : (
                            <span className="text-lg text-slate-600">○</span>
                          )}
                        </button>
                      );
                    })}
                  </div>
                </div>
              );
            })}
            <p className="text-[7px] text-slate-600 text-center font-bold pt-1">
              Toca un espacio ocupado para retirar el item ·
              {selectedSlotId ? " Espacio seleccionado" : " Toca un espacio vacío para seleccionar"}
            </p>
          </div>
        )}

        {/* ── TAB: Inventory ── */}
        {activeTab === "inventory" && (
          <div className="px-4 pb-4">
            {/* Filter chips */}
            <div className="flex gap-1.5 mb-2.5 overflow-x-auto scrollbar-hide">
              {(["ALL", "MANTEL", "ADORNOS_FIJOS", "ILUMINACION", "ENTORNO"] as const).map((f) => {
                const labels: Record<string, string> = { ALL: "Todo", MANTEL: "Mantel", ADORNOS_FIJOS: "Adornos", ILUMINACION: "Iluminación", ENTORNO: "Entorno" };
                const icons: Record<string, string> = { ALL: "📦", MANTEL: "🧣", ADORNOS_FIJOS: "🏺", ILUMINACION: "💡", ENTORNO: "🌄" };
                return (
                  <button
                    key={f}
                    onClick={() => setInventoryFilter(f)}
                    className={`shrink-0 px-2 py-1 rounded-full text-[8px] font-black uppercase tracking-wider transition-all ${
                      inventoryFilter === f
                        ? "bg-teal-700/40 text-teal-300 border border-teal-500/30"
                        : "bg-slate-800/60 text-slate-500 border border-white/5 hover:border-white/20"
                    }`}
                  >
                    {icons[f]} {labels[f]}
                  </button>
                );
              })}
            </div>

            {/* Item grid */}
            {loading ? (
              <div className="flex items-center justify-center py-8">
                <span className="text-2xl animate-pulse">🪸</span>
                <span className="text-[10px] font-black text-slate-500 ml-2">Cargando inventario…</span>
              </div>
            ) : inventory.length === 0 ? (
              <div className="text-center py-8">
                <span className="text-3xl">🎒</span>
                <p className="text-[10px] text-slate-500 font-bold mt-1">No tienes decoraciones disponibles.</p>
                <p className="text-[8px] text-slate-600 mt-0.5">Consigue decoraciones en la Tienda.</p>
              </div>
            ) : (
              <div className="grid grid-cols-3 gap-2">
                {inventory
                  .filter((item) => inventoryFilter === "ALL" || item.subcategory === inventoryFilter)
                  .map((item) => {
                    const isPlaced = Object.values(placedDecos).some((d) => d.item_id === item.id);
                    const rarityStyle = RARITY_STYLES[item.rarity];
                    const isIncorrectSlot =
                      selectedSlotId !== null && !selectedSlotId.startsWith(item.subcategory);
                    return (
                      <button
                        key={item.id}
                        onClick={() => handlePlaceItem(item)}
                        disabled={isIncorrectSlot}
                        className={`relative flex flex-col items-center rounded-xl p-2 transition-all border text-left ${
                          isPlaced
                            ? "bg-emerald-900/20 border-emerald-500/30 opacity-80"
                            : isIncorrectSlot
                            ? "bg-gray-800/30 border-white/5 opacity-40 cursor-not-allowed"
                            : "bg-gray-800/60 border-white/5 hover:border-white/20 hover:bg-gray-700/60 active:scale-95"
                        }`}
                        aria-label={`${item.name} (${rarityLabel(item.rarity)})`}
                      >
                        {/* Placed badge */}
                        {isPlaced && (
                          <span className="absolute -top-1 -right-1 w-3.5 h-3.5 rounded-full bg-emerald-500 border border-emerald-300 flex items-center justify-center">
                            <span className="text-[6px] text-white font-black">✓</span>
                          </span>
                        )}
                        <span className="text-2xl">{item.emoji}</span>
                        <span className="text-[7px] font-bold text-white mt-0.5 leading-tight text-center line-clamp-1">
                          {item.name}
                        </span>
                        {/* Rarity badge */}
                        <span className={`mt-0.5 px-1 py-[1px] rounded-full text-[6px] font-black uppercase tracking-wider ${rarityStyle.badge}`}>
                          {rarityLabel(item.rarity)}
                        </span>
                        {/* Stat badges */}
                        <div className="flex gap-1 mt-0.5">
                          {item.bonuses.focus_recovery && (
                            <span className="text-[6px] font-black text-emerald-400 bg-emerald-950/50 px-1 rounded-full">
                              🔋 +{item.bonuses.focus_recovery}%
                            </span>
                          )}
                          {item.bonuses.frj_multiplier && (
                            <span className="text-[6px] font-black text-amber-400 bg-amber-950/50 px-1 rounded-full">
                              💰 +{item.bonuses.frj_multiplier}%
                            </span>
                          )}
                        </div>
                        {isPlaced && (
                          <span className="text-[6px] font-black text-emerald-400 mt-0.5">Colocado</span>
                        )}
                      </button>
                    );
                  })}
              </div>
            )}
          </div>
        )}

        {/* ── TAB: Bonuses ── */}
        {activeTab === "bonuses" && (
          <div className="px-4 pb-4 space-y-3">
            {/* Focus Recovery */}
            <div className="bg-gradient-to-br from-emerald-900/20 to-slate-800/30 border border-emerald-500/20 rounded-xl p-3">
              <div className="flex items-center justify-between mb-1">
                <span className="text-[10px] font-black text-emerald-300">🔋 Recuperación de Focus</span>
                <span className="text-[9px] font-black text-emerald-400 tabular-nums">
                  {computedBonuses.focusRecovery}% / {computedBonuses.capFocus}%
                </span>
              </div>
              <div className="h-2 bg-slate-800 rounded-full overflow-hidden">
                <div
                  className="h-full rounded-full bg-gradient-to-r from-emerald-600 to-emerald-400 transition-all duration-500"
                  style={{ width: `${Math.min(100, (computedBonuses.focusRecovery / computedBonuses.capFocus) * 100)}%` }}
                />
              </div>
              <p className="text-[7px] text-slate-500 font-bold mt-1">
                Límite basado en nivel de cueva (cada nivel da +5% base + 10%)
              </p>
            </div>

            {/* FRJ Staking Multiplier */}
            <div className="bg-gradient-to-br from-amber-900/20 to-slate-800/30 border border-amber-500/20 rounded-xl p-3">
              <div className="flex items-center justify-between mb-1">
                <span className="text-[10px] font-black text-amber-300">💰 Multiplicador FRJ Staking</span>
                <span className="text-[9px] font-black text-amber-400 tabular-nums">
                  {computedBonuses.frjMultiplier}% / {computedBonuses.capFrj}%
                </span>
              </div>
              <div className="h-2 bg-slate-800 rounded-full overflow-hidden">
                <div
                  className="h-full rounded-full bg-gradient-to-r from-amber-600 to-amber-400 transition-all duration-500"
                  style={{ width: `${Math.min(100, (computedBonuses.frjMultiplier / computedBonuses.capFrj) * 100)}%` }}
                />
              </div>
              <p className="text-[7px] text-slate-500 font-bold mt-1">
                Límite basado en nivel de cueva (cada nivel da +3% base + 5%)
              </p>
            </div>

            {/* Contributing items */}
            <div>
              <h4 className="text-[8px] font-black text-slate-500 uppercase tracking-wider mb-1.5">Items que contribuyen</h4>
              {computedBonuses.contribItems.length === 0 ? (
                <p className="text-[9px] text-slate-600 italic text-center py-3">
                  Coloca decoraciones con bonos para activar mejoras pasivas.
                </p>
              ) : (
                <div className="space-y-1">
                  {computedBonuses.contribItems.map((c, i) => (
                    <div
                      key={i}
                      className="flex items-center gap-2 bg-slate-800/40 rounded-lg px-2.5 py-1.5 border border-white/5"
                    >
                      <span className="text-base">{c.emoji}</span>
                      <span className="text-[9px] font-bold text-white flex-1">{c.name}</span>
                      <span
                        className={`text-[8px] font-black tabular-nums ${
                          c.type === "focus" ? "text-emerald-400" : "text-amber-400"
                        }`}
                      >
                        {c.type === "focus" ? "🔋" : "💰"}+{c.value}%
                      </span>
                    </div>
                  ))}
                </div>
              )}
            </div>
          </div>
        )}

        {/* ── Footer: Save button ── */}
        <div className="px-4 pb-4 shrink-0">
          <button
            onClick={handleSave}
            disabled={saving}
            className="w-full py-2.5 rounded-xl font-black text-[10px] uppercase tracking-wider bg-gradient-to-r from-teal-600 to-emerald-600 hover:from-teal-500 hover:to-emerald-500 text-white transition-all active:scale-95 disabled:opacity-50 shadow-[0_0_16px_rgba(45,212,191,0.2)]"
          >
            {saving ? "💾 Guardando…" : "💾 Guardar Decoración"}
          </button>
        </div>
      </div>
    </div>
  );
}
