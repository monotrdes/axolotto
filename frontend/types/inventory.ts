// ═══════════════════════════════════════════════════════
// TYPES — Inventory
// ═══════════════════════════════════════════════════════

export interface InventoryItem {
  id: number;
  inventory_id?: number;
  item_type?: string;
  name?: string;
  quantity: number;
  is_shiny?: boolean;
  is_first_edition?: boolean;
  is_listed?: boolean;
  item_metadata?: Record<string, any>;
  dynamic_rarity?: string;
  description?: string;
  circulation?: number;
}

export interface CardItem {
  id: number;
  name: string;
  description?: string;
  dynamic_rarity?: string;
  is_shiny?: boolean;
  is_first_edition?: boolean;
  item_metadata?: {
    numero_loteria?: number | string;
    [key: string]: any;
  };
  circulation?: number;
  availableQty?: number;
}

export interface Axolotito {
  id: number;
  blockchain_token_id?: number;
  name: string;
  level: number;
  skin_color: string;
  gill_type: string;
  eye_type: string;
  mouth_type: string;
  tail_type: string;
  forehead_type: string;
  limb_type: string;
  stat_luck: number;
  stat_focus: number;
  stat_stamina: number;
  stat_salinity: number;
  energy_current: number;
  dna_sequence?: string;
  equipped_head_item_id?: number | null;
  equipped_eyes_item_id?: number | null;
  equipped_body_item_id?: number | null;
}

export interface PlayerBoard {
  id: number;
  name: string;
  user_id: string;
  level: number;
  xp: number;
  card_ids: (number | null)[];
  csr: number;
  suerte_tag: string;
  games_played: number;
  games_won: number;
  win_rate: number;
  hourly_yield_gal: number;
  accrued_staking_gal: number;
  is_rented?: boolean;
  is_listed_for_rent?: boolean;
  is_tutorial?: boolean;
  rent_expires_at?: string;
  rent_fee_gal?: number;
  rent_share_owner_pct?: number;
  slot_generation?: number;
}

export interface SlotRequirements {
  slot_number: number;
  cost_gal: number;
  games_played_required: number;
  games_won_required: number;
  can_unlock: boolean;
  reasons?: string[];
}

export interface SlotsStatus {
  unlocked_slots: number;
  used_slots: number;
  total_games_played: number;
  total_games_won: number;
  current_gal: number;
  next_slot_requirements?: SlotRequirements;
  slots_xp?: Record<number, { preserved_xp: number; preserved_level: number }>;
}

export interface CatalogItem {
  id: number;
  name: string;
  description?: string;
  item_metadata?: Record<string, any>;
  quantity?: number;
  [key: string]: any;
}

export type CardRarityFilter = 'all' | 'comun' | 'poco_comun' | 'rara' | 'epica' | 'legendaria';
export type CardShinyFilter = 'all' | 'shiny' | 'normal';
export type CardOwnedFilter = 'all' | 'owned' | 'not_owned';
export type InventoryMode = 'cartas' | 'axolotitos' | 'tablas' | 'items';
export type MochilaTab = 'cartas' | 'tablas' | 'items';
