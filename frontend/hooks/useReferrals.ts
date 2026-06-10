"use client";

import { useState, useCallback } from "react";
import axios from "axios";
import { API_BASE } from "@/lib/api";

export interface ReferralDashboard {
  code: string;
  total_uses: number;
  active_referrals: number;
  rewards_earned_frj: number;
  max_active: number;
  max_lifetime: number;
  referred_users: ReferredUser[];
}

export interface ReferredUser {
  referred_id: string;
  nickname: string | null;
  status: string;
  referred_at: string;
  converted_at: string | null;
}

export function useReferrals(token: string | null) {
  const [dashboard, setDashboard] = useState<ReferralDashboard | null>(null);
  const [loading, setLoading] = useState(false);

  const headers = useCallback(
    () => ({ Authorization: `Bearer ${token}` }),
    [token]
  );

  const fetchCode = useCallback(async () => {
    if (!token) return null;
    try {
      const res = await axios.get(`${API_BASE}/referrals/code`, {
        headers: headers(),
      });
      return res.data as { code: string; total_uses: number; share_link: string };
    } catch (e) {
      console.error("Error fetching referral code:", e);
      return null;
    }
  }, [token]);

  const claimReferral = useCallback(
    async (code: string) => {
      if (!token) return null;
      const res = await axios.post(
        `${API_BASE}/referrals/claim`,
        { code },
        { headers: headers() }
      );
      return res.data;
    },
    [token]
  );

  const reportMilestone = useCallback(
    async (milestone: string) => {
      if (!token) return null;
      try {
        const res = await axios.post(
          `${API_BASE}/referrals/milestone`,
          { milestone },
          { headers: headers() }
        );
        return res.data;
      } catch (e) {
        console.error("Error reporting milestone:", e);
        return null;
      }
    },
    [token]
  );

  const fetchDashboard = useCallback(async () => {
    if (!token) return null;
    setLoading(true);
    try {
      const res = await axios.get(`${API_BASE}/referrals/dashboard`, {
        headers: headers(),
      });
      setDashboard(res.data);
      return res.data as ReferralDashboard;
    } catch (e) {
      console.error("Error fetching referral dashboard:", e);
      return null;
    } finally {
      setLoading(false);
    }
  }, [token]);

  return {
    dashboard,
    loading,
    fetchCode,
    claimReferral,
    reportMilestone,
    fetchDashboard,
  };
}
