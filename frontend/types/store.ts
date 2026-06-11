// ═══════════════════════════════════════════════════════
// TYPES — Store / Tianguis
// ═══════════════════════════════════════════════════════

export type StoreTab = 'official' | 'market' | 'melter';

export type UnboxingPhase = 'pack' | 'opening' | 'reveal' | 'summary';

export type CapsuleTier = 'bronce' | 'plata' | 'oro';

export interface StoreItem {
  id: number;
  name: string;
  description?: string;
  price_axg?: number;
  price_gal?: number;
  item_type: string;
  item_metadata?: Record<string, any>;
  is_active?: boolean;
  total_sold?: number;
  max_supply?: number;
  user_owned?: number;
  // Nido availability — populated by backend for egg items
  sin_nidos?: boolean;
  max_nidos?: number;
  nidos_libres?: number;
  total_huevos?: number;
}

export interface CardItem {
  id: number;
  name: string;
  dynamic_rarity?: string;
  is_shiny?: boolean;
  item_metadata?: Record<string, any>;
  [key: string]: any;
}

export interface PackTheme {
  accentColor: string;
  gradient: string;
  borderColor: string;
  glowColor: string;
  packLabel: string;
  cardBackGradient: string;
  cardBackBorder: string;
  cardBackSymbol: string;
  modalBorder: string;
  modalGlow: string;
  titleText: string;
}

export interface CapsuleResult {
  tier?: string;
  outcome_type?: string;
  item?: StoreItem;
  gal_rewarded?: number;
  results?: CapsuleResult[];
  [key: string]: any;
}

export interface StoreProps {
  userId: string;
  balances: any;
  token: string | null;
  cambiarTab: (tab: any) => void;
  recargarSaldos: () => void;
  /** Mundo papel picado: sección a abrir al tocar un puesto del Tianguis. */
  initialSection?: StoreTab;
  /** Nonce para re-disparar initialSection aunque sea la misma sección. */
  sectionNonce?: number;
  [key: string]: any;
}

export interface AdoptionParticle {
  id: number;
  content: string;
  color: string;
  size: number;
  left: number;
  delay: number;
  duration: number;
  drift: number;
  rot: number;
}
