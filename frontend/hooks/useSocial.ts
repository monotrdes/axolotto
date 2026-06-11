"use client";

import { useState, useCallback } from "react";
import axios from "axios";
import { API_BASE } from "@/lib/api";

// ── Types ───────────────────────────────────────────────────────────────────

export interface FriendInfo {
  relation_id: number;
  friend_id: string;
  nickname: string | null;
  avatar_url: string;
  vip_tier: string | null;
  is_online: boolean;
  is_best_friend: boolean;
  interaction_count: number;
  friends_since: string | null;
}

export interface FriendRequestInfo {
  id: number;
  from_user_id: string;
  from_nickname: string | null;
  from_avatar_url: string;
  created_at: string;
}

export interface SentRequestInfo {
  id: number;
  to_user_id: string;
  to_nickname: string | null;
  to_avatar_url: string;
  created_at: string;
}

export interface PlayerResult {
  user_id: string;
  nickname: string | null;
  avatar_url: string;
  vip_tier: string | null;
  cave_level?: number;
  friendship_status: string;
  mutual_friends?: number;
}

export interface FriendCave {
  friend_id: string;
  nickname: string | null;
  cave_name: string | null;
  cave_level: number;
  cave_decorations: string | null;
  vip_tier: string | null;
  avatar_url: string;
  is_online: boolean;
}

// ── Hook ────────────────────────────────────────────────────────────────────

export function useSocial(token: string | null) {
  const [friends, setFriends] = useState<FriendInfo[]>([]);
  const [pendingRequests, setPendingRequests] = useState<FriendRequestInfo[]>([]);
  const [sentRequests, setSentRequests] = useState<SentRequestInfo[]>([]);
  const [loading, setLoading] = useState(false);

  const headers = useCallback(() => ({
    Authorization: `Bearer ${token}`,
  }), [token]);

  // ── Friends list ──────────────────────────────────────────────────────

  const fetchFriends = useCallback(async () => {
    if (!token) return [];
    setLoading(true);
    try {
      const res = await axios.get(`${API_BASE}/social/friends`, { headers: headers() });
      setFriends(res.data);
      return res.data as FriendInfo[];
    } catch (e) {
      console.error("Error fetching friends:", e);
      return [];
    } finally {
      setLoading(false);
    }
  }, [token]);

  const fetchTopFriends = useCallback(async (limit = 4) => {
    if (!token) return [];
    try {
      const res = await axios.get(`${API_BASE}/social/friends/top`, {
        headers: headers(),
        params: { limit },
      });
      return res.data as FriendInfo[];
    } catch (e) {
      console.error("Error fetching top friends:", e);
      return [];
    }
  }, [token]);

  // ── Friend requests ───────────────────────────────────────────────────

  const fetchPendingRequests = useCallback(async () => {
    if (!token) return [];
    try {
      const res = await axios.get(`${API_BASE}/social/friends/pending`, { headers: headers() });
      setPendingRequests(res.data);
      return res.data as FriendRequestInfo[];
    } catch (e) {
      console.error("Error fetching pending requests:", e);
      return [];
    }
  }, [token]);

  const fetchSentRequests = useCallback(async () => {
    if (!token) return [];
    try {
      const res = await axios.get(`${API_BASE}/social/friends/sent`, { headers: headers() });
      setSentRequests(res.data);
      return res.data as SentRequestInfo[];
    } catch (e) {
      console.error("Error fetching sent requests:", e);
      return [];
    }
  }, [token]);

  const sendFriendRequest = useCallback(async (targetUserId: string) => {
    if (!token) throw new Error("No token");
    const res = await axios.post(
      `${API_BASE}/social/friends/request`,
      { target_user_id: targetUserId },
      { headers: headers() }
    );
    return res.data;
  }, [token]);

  const acceptFriendRequest = useCallback(async (requestId: number) => {
    if (!token) throw new Error("No token");
    const res = await axios.post(
      `${API_BASE}/social/friends/accept/${requestId}`,
      null,
      { headers: headers() }
    );
    await fetchPendingRequests();
    await fetchFriends();
    return res.data;
  }, [token, fetchPendingRequests, fetchFriends]);

  const rejectFriendRequest = useCallback(async (requestId: number) => {
    if (!token) throw new Error("No token");
    const res = await axios.post(
      `${API_BASE}/social/friends/reject/${requestId}`,
      null,
      { headers: headers() }
    );
    await fetchPendingRequests();
    return res.data;
  }, [token, fetchPendingRequests]);

  const removeFriend = useCallback(async (relationId: number) => {
    if (!token) throw new Error("No token");
    await axios.delete(`${API_BASE}/social/friends/${relationId}`, { headers: headers() });
    await fetchFriends();
  }, [token, fetchFriends]);

  // ── Search & Discovery ────────────────────────────────────────────────

  const searchPlayers = useCallback(async (query: string): Promise<PlayerResult[]> => {
    if (!token || query.length < 2) return [];
    try {
      const res = await axios.get(`${API_BASE}/social/friends/search`, {
        headers: headers(),
        params: { q: query },
      });
      return res.data;
    } catch (e) {
      console.error("Error searching players:", e);
      return [];
    }
  }, [token]);

  const getRecentPlayers = useCallback(async (): Promise<PlayerResult[]> => {
    if (!token) return [];
    try {
      const res = await axios.get(`${API_BASE}/social/friends/recent-players`, { headers: headers() });
      return res.data;
    } catch (e) {
      console.error("Error fetching recent players:", e);
      return [];
    }
  }, [token]);

  const getSuggestions = useCallback(async (): Promise<PlayerResult[]> => {
    if (!token) return [];
    try {
      const res = await axios.get(`${API_BASE}/social/friends/suggestions`, { headers: headers() });
      return res.data;
    } catch (e) {
      console.error("Error fetching suggestions:", e);
      return [];
    }
  }, [token]);

  // ── Social Actions ────────────────────────────────────────────────────

  const sendLike = useCallback(async (targetUserId: string) => {
    if (!token) throw new Error("No token");
    const res = await axios.post(
      `${API_BASE}/social/like/${targetUserId}`,
      null,
      { headers: headers() }
    );
    return res.data;
  }, [token]);

  const visitCave = useCallback(async (friendId: string): Promise<FriendCave | null> => {
    if (!token) return null;
    try {
      const res = await axios.post(
        `${API_BASE}/social/visit/${friendId}`,
        null,
        { headers: headers() }
      );
      return res.data;
    } catch (e) {
      console.error("Error visiting cave:", e);
      return null;
    }
  }, [token]);

  const getFriendCave = useCallback(async (friendId: string): Promise<FriendCave | null> => {
    if (!token) return null;
    try {
      const res = await axios.get(`${API_BASE}/social/friends/${friendId}/cave`, {
        headers: headers(),
      });
      return res.data;
    } catch (e) {
      console.error("Error fetching friend cave:", e);
      return null;
    }
  }, [token]);

  const blockUser = useCallback(async (userId: string) => {
    if (!token) throw new Error("No token");
    await axios.post(
      `${API_BASE}/social/friends/block`,
      { user_id: userId },
      { headers: headers() }
    );
    await fetchFriends();
  }, [token, fetchFriends]);

  const togglePinFriend = useCallback(async (friendId: string, pinned: boolean) => {
    if (!token) throw new Error("No token");
    const res = await axios.post(
      `${API_BASE}/social/friends/pin/${friendId}`,
      null,
      {
        headers: headers(),
        params: { pinned },
      }
    );
    await fetchFriends();
    return res.data;
  }, [token, fetchFriends]);

  return {
    friends,
    pendingRequests,
    sentRequests,
    loading,
    fetchFriends,
    fetchTopFriends,
    fetchPendingRequests,
    fetchSentRequests,
    sendFriendRequest,
    acceptFriendRequest,
    rejectFriendRequest,
    removeFriend,
    searchPlayers,
    getRecentPlayers,
    getSuggestions,
    sendLike,
    visitCave,
    getFriendCave,
    blockUser,
    togglePinFriend,
  };
}
