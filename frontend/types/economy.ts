// ═══════════════════════════════════════════════════════
// TYPES — Economy (staking, daily claim, F2P rewards)
// ═══════════════════════════════════════════════════════

export interface StakingAxolotitoInfo {
  id: number;
  name: string;
  hourly_rate: number;
  accrued_unclaimed: number;
  cap_reached: boolean;
  play_to_stake_active: boolean;
}

export interface StakingStatus {
  slots_total: number;
  slots_used: number;
  axolotitos: StakingAxolotitoInfo[];
  total_accrued: number;
}

export interface DailyClaimStatus {
  can_claim: boolean;
  amount: number;
  streak: number;
  is_streak_max: boolean;
  next_claim_at: string;
}

export interface LunarTodayReward {
  type: 'frj' | 'capsule';
  amount?: number;
  capsules?: Array<{ tier: string; qty: number }>;
}

export interface LunarDayReward {
  capsules: Array<{ tier: string; qty: number }>;
  label: string;
}

export interface LunaTrackItem {
  luna: number;          // 1-6
  completed: boolean;
  is_current: boolean;
  reward_label: string;
}

export interface LunarStatus {
  lunar_week: number;         // 1-6, current Luna
  streak_day: number;         // 0-6, days already claimed this week (0=none yet)
  can_claim: boolean;
  today_reward: LunarTodayReward;
  day7_reward: LunarDayReward;
  next_claim_at: string | null;
  luna_track: LunaTrackItem[];
  cycles_completed: number;
}

export interface LunarClaimResult {
  type: 'frj' | 'capsule';
  amount?: number;
  rolls?: unknown[];          // capsule roll results
  streak_day: number;
  lunar_week: number;
  cycles_completed: number;
  cycle_complete?: boolean;
}
