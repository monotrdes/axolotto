/** Estado de la cueva que el diorama necesita (de GET /cave/status). */
export interface CaveStatusData {
  level: number;
  spots: number;
  hasTable: boolean;
  tableSeats: number;
}

/** Payload de GET /cave/decorations que consume el diorama. */
export interface DecorSlotInfo {
  slot_id: string;
  subcategory: string;
}
export interface DecorItemDetail {
  name?: string;
  emoji?: string;
  color?: string | null;
}
export interface DecoracionesData {
  decorations: Record<string, number | null>;
  slots: DecorSlotInfo[];
  items: Record<string, DecorItemDetail>;
}
