// ═══════════════════════════════════════════════════════
// TYPES — VIP
// ═══════════════════════════════════════════════════════

export interface VipStatus {
  is_vip: boolean;
  vip_tier: string | null;
  vip_expires_at: string | null;
  days_remaining: number | null;
  vip_streak_months: number;
  vip_pending_gal: number;
  pending_gal_expires_at: string | null;
  benefits: Record<string, unknown>;
  vip_tiers_activated: string[];
  vip_auto_renew?: boolean;
}

export interface VipNotification {
  id: number;
  type: "activation" | "claim";
  tier?: string;
  welcome_gal?: number;
  claimed_gal?: number;
  is_first_activation?: boolean;
}
