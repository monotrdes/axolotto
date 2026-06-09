// ═══════════════════════════════════════════════════════
// API SERVICE — Santuario
// ═══════════════════════════════════════════════════════
import axios from 'axios';
import { API_BASE } from '@/lib/api';

const API = `${API_BASE}`;

function headers(token: string | null) {
  return token ? { Authorization: `Bearer ${token}` } : {};
}

// ── Cave status ──
export async function fetchCaveStatus(userId: string, token: string | null) {
  const res = await axios.get(`${API}/cave/status?user_id=${userId}`, { headers: headers(token) });
  return res.data;
}

// ── Cave expansion ──
export async function expandCave(token: string | null) {
  const res = await axios.post(`${API}/cave/expand`, {}, { headers: headers(token) });
  return res.data;
}

export async function accelerateCave(token: string | null) {
  const res = await axios.post(`${API}/cave/expand/accelerate`, {}, { headers: headers(token) });
  return res.data;
}

// ── Incubaciones ──
export async function fetchIncubaciones(userId: string, token: string | null) {
  const res = await axios.get(`${API}/incubation/user/${userId}`, { headers: headers(token) });
  return res.data;
}

// ── Axolotitos ──
export async function fetchAxolotitos(userId: string, token: string | null) {
  const res = await axios.get(`${API}/auth/axolotitos/${userId}`, { headers: headers(token) });
  return res.data || [];
}

// ── Hatch egg ──
export async function hatchEgg(incId: number, token: string | null) {
  const res = await axios.post(`${API}/incubation/hatch/${incId}`, {}, { headers: headers(token) });
  return res.data;
}

// ── Set main axolotito ──
export async function setMainAxolotito(axoId: number, token: string | null) {
  await axios.post(`${API}/auth/axolotitos/${axoId}/set-main`, {}, { headers: headers(token) });
}

// ── Feed axolotito ──
export async function feedAxolotito(axoId: number, foodType: string, token: string | null) {
  await axios.post(`${API}/game/axolotitos/${axoId}/feed`, { food_type: foodType }, { headers: headers(token) });
}

// ── Sleep axolotito ──
export async function sleepAxolotito(axoId: number, token: string | null) {
  await axios.post(`${API}/game/axolotitos/${axoId}/sleep`, {}, { headers: headers(token) });
}

// ── Legacy ──
export async function fetchLegacyStatus(userId: string, token: string | null) {
  const res = await axios.get(`${API}/legacy/status?user_id=${userId}`, { headers: headers(token) });
  return res.data;
}

export async function claimLegacy(userId: string, token: string | null) {
  const res = await axios.post(`${API}/legacy/claim?user_id=${userId}`, {}, { headers: headers(token) });
  return res.data;
}

// ── Inventory ──
export async function fetchInventory(userId: string, token: string | null) {
  const res = await axios.get(`${API}/auth/inventory/${userId}`, { headers: headers(token) });
  return res.data;
}

// ── Shop items ──
export async function fetchShopItems() {
  const res = await axios.get(`${API}/shop/items`);
  return res.data;
}

// ── Cave room ──
export async function fetchCaveData(axoId: number, token: string | null) {
  const res = await axios.get(`${API}/game/axolotitos/${axoId}/cave`, { headers: headers(token) });
  return res.data;
}

export async function equipCaveItem(axoId: number, itemId: number, token: string | null) {
  await axios.post(`${API}/game/axolotitos/${axoId}/cave/equip`, { item_id: itemId }, { headers: headers(token) });
}

export async function unequipCaveItem(axoId: number, itemId: number, token: string | null) {
  await axios.post(`${API}/game/axolotitos/${axoId}/cave/unequip`, { item_id: itemId }, { headers: headers(token) });
}

// ── Shield / incubation items ──
export async function useIncubationItem(incId: number, itemId: number, userId: string, token: string | null) {
  await axios.post(`${API}/incubation/use-item/${incId}?item_id=${itemId}&user_id=${userId}`, {}, { headers: headers(token) });
}

export async function buyAndUseIncubationItem(incId: number, itemId: number, userId: string, token: string | null) {
  await axios.post(`${API}/incubation/buy-and-use/${incId}?item_id=${itemId}&user_id=${userId}`, {}, { headers: headers(token) });
}

// ── Staking ──
export async function fetchStakingStatus(userId: string, token: string | null) {
  const res = await axios.get(`${API}/staking/status?user_id=${userId}`, { headers: headers(token) });
  return res.data;
}

export async function claimAxolotitoStaking(axolotitoId: number, token: string | null) {
  const res = await axios.post(`${API}/staking/claim/${axolotitoId}`, {}, { headers: headers(token) });
  return res.data;
}

export async function claimAllStaking(token: string | null) {
  const res = await axios.post(`${API}/staking/claim-all`, {}, { headers: headers(token) });
  return res.data;
}

export async function stakeAxolotito(axolotitoId: number, status: 'studying' | 'resting', token: string | null) {
  const res = await axios.post(`${API}/staking/stake/${axolotitoId}?status=${status}`, {}, { headers: headers(token) });
  return res.data;
}

export async function unstakeAxolotito(axolotitoId: number, token: string | null) {
  const res = await axios.post(`${API}/staking/unstake/${axolotitoId}`, {}, { headers: headers(token) });
  return res.data;
}

// ── Imprinting / Padrinos ──
export async function startImprinting(incId: number, padrinoId: number, token: string | null) {
  const res = await axios.post(
    `${API}/incubation/start-imprinting`,
    { incubation_id: incId, padrino_axolotito_id: padrinoId },
    { headers: headers(token) }
  );
  return res.data;
}

export async function fetchImprintingStatus(incId: number, token: string | null) {
  const res = await axios.get(`${API}/incubation/imprinting-status/${incId}`, { headers: headers(token) });
  return res.data;
}

// ── Arcade (Cenote minigame) ──
export async function submitArcadeScore(score: number, token: string | null) {
  const res = await axios.post(`${API}/cave/minigames/arcade/play`, { score }, { headers: headers(token) });
  return res.data;
}

export async function fetchArcadeLeaderboard(token: string | null) {
  const res = await axios.get(`${API}/cave/minigames/arcade/leaderboard`, { headers: headers(token) });
  return res.data;
}

// ── Wishing Well ──
export async function playWishingWell(accuracy: number, outcome: string, token: string | null) {
  const res = await axios.post(`${API}/cave/minigames/wishing-well`, {}, { headers: headers(token) });
  return res.data;
}

