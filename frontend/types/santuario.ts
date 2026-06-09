// ═══════════════════════════════════════════════════════
// TYPES — Santuario
// ═══════════════════════════════════════════════════════
export type SpotType = 'egg' | 'axo' | 'empty' | 'bed';
export type SpotSlot = { type: SpotType; data: any };
export type SelectedSlot = SpotSlot;

export interface AxoPos {
  left: number; bottom: number; depth: number;
  duration: number; delay: number; driftX: number;
}

export interface CaveItem {
  id: number;
  name: string;
  rarity?: string;
  item_metadata?: Record<string, any>;
}

export interface CaveData {
  axo_id: number;
  cave_items: CaveItem[];
  max_slots: number;
}

export interface InventoryItem {
  id?: number;
  item_id?: number;
  quantity: number;
  name?: string;
  rarity?: string;
  item_type?: string;
  item_metadata?: Record<string, any>;
}

export interface ShieldModalProps {
  incId: number;
  incubaciones: any[];
  userId: string;
  token: string | null;
  cantidadGotas: number;
  cantidadLamparas: number;
  precioGotas: number;
  precioLamparas: number;
  onClose: () => void;
  onSuccess: () => void;
  cambiarTab?: (tab: string) => void;
}
