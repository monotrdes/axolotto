// ═══════════════════════════════════════════════════════
// API SERVICE — F2P Rewards (daily claim)
// ═══════════════════════════════════════════════════════
import axios from 'axios';
import { API_BASE } from '@/lib/api';
import type { DailyClaimStatus, LunarStatus, LunarClaimResult } from '@/types/economy';

const API = `${API_BASE}`;

function authHeaders(token: string | null) {
  return token ? { Authorization: `Bearer ${token}` } : {};
}

/** Fetch daily claim status (can_claim, amount, streak, next_claim_at) */
export async function fetchDailyClaimStatus(token: string): Promise<DailyClaimStatus> {
  const res = await axios.get(`${API}/rewards/daily-claim/status`, {
    headers: authHeaders(token),
  });
  return res.data;
}

/** Claim the daily FRJ reward. Returns { amount, streak, new_balance } */
export async function claimDailyReward(
  token: string,
): Promise<{ amount: number; streak: number; new_balance: number }> {
  const res = await axios.post(
    `${API}/rewards/daily-claim`,
    {},
    { headers: authHeaders(token) },
  );
  return res.data;
}

/** Fetch Ciclo Lunar status */
export async function fetchLunarStatus(token: string): Promise<LunarStatus> {
  const res = await axios.get(`${API}/rewards/lunar/status`, {
    headers: authHeaders(token),
  });
  return res.data;
}

/** Claim today's Ciclo Lunar reward (FRJ days 1-6, or capsule(s) on day 7) */
export async function claimLunarDay(token: string): Promise<LunarClaimResult> {
  const res = await axios.post(
    `${API}/rewards/lunar/claim`,
    {},
    { headers: authHeaders(token) },
  );
  return res.data;
}
