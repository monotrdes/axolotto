// ═══════════════════════════════════════════════════════
// API SERVICE — Store (Tianguis)
// ═══════════════════════════════════════════════════════
import axios from 'axios';
import { API_BASE } from '@/lib/api';
import type { CapsuleTier } from '@/types/store';

const API = `${API_BASE}`;

function authHeaders(token: string | null) {
  return token ? { Authorization: `Bearer ${token}` } : {};
}

// ── Items / Shop ──

export async function fetchShopItems(userId: string) {
  const res = await axios.get(`${API}/shop/items?user_id=${userId}`);
  return res.data;
}

export async function fetchShopCards() {
  const res = await axios.get(`${API}/shop/cards`);
  return res.data;
}

export async function fetchUserInventory(userId: string, token: string | null) {
  const res = await axios.get(`${API}/auth/inventory/${userId}`, {
    headers: authHeaders(token),
  });
  return res.data;
}

export async function buyItem(
  userId: string,
  itemId: number,
  moneda: string,
  token: string | null,
) {
  const res = await axios.post(
    `${API}/shop/buy`,
    {
      user_id: userId,
      item_id: itemId,
      payment_currency: moneda,
    },
    {
      headers: {
        Authorization: `Bearer ${token}`,
        'Content-Type': 'application/json',
      },
    },
  );
  return res.data;
}

export async function openBooster(
  itemId: number,
  token: string | null,
) {
  const res = await axios.post(
    `${API}/shop/booster/open`,
    { item_id: itemId },
    {
      headers: {
        Authorization: `Bearer ${token}`,
        'Content-Type': 'application/json',
      },
    },
  );
  return res.data;
}

// ── Capsules / Gashapon ──

export async function rollCapsule(tier: CapsuleTier, token: string | null) {
  const res = await axios.post(
    `${API}/shop/capsule/roll`,
    { tier },
    { headers: authHeaders(token) },
  );
  return res.data;
}

export async function rollTripleSuerte(token: string | null) {
  const res = await axios.post(
    `${API}/shop/capsule/triple-suerte`,
    {},
    { headers: authHeaders(token) },
  );
  return res.data;
}

export async function fetchCapsuleFeed() {
  const res = await axios.get(`${API}/shop/capsule/feed`);
  return res.data;
}

// ── Cave expansion (nido purchase from store) ──

export async function expandCave(token: string | null) {
  const res = await axios.post(
    `${API}/cave/expand?path=pago`,
    {},
    { headers: authHeaders(token) },
  );
  return res.data;
}
