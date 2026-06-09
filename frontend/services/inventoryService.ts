// ═══════════════════════════════════════════════════════
// API SERVICE — Inventory
// ═══════════════════════════════════════════════════════
import axios from 'axios';
import { API_BASE } from '@/lib/api';

const API = API_BASE;

function authHeaders(token: string | null) {
  return token ? { Authorization: `Bearer ${token}` } : {};
}

// ── Inventory / User Data ──
export async function fetchInventory(userId: string, token: string | null) {
  const res = await axios.get(`${API}/auth/inventory/${userId}`, { headers: authHeaders(token) });
  return res.data;
}

export async function fetchCardsCatalog() {
  const res = await axios.get(`${API}/shop/cards`);
  return res.data;
}

export async function fetchAxolotitos(userId: string, token: string | null) {
  const res = await axios.get(`${API}/auth/axolotitos/${userId}`, { headers: authHeaders(token) });
  return res.data;
}

export async function fetchShopItems() {
  const res = await axios.get(`${API}/shop/items`);
  return res.data;
}

export async function fetchPlayerBoards(userId: string, token: string | null) {
  const res = await axios.get(`${API}/board/user/${userId}`, { headers: authHeaders(token) });
  return res.data;
}

export async function fetchSlotsStatus(token: string | null) {
  const res = await axios.get(`${API}/board/slots/status`, { headers: authHeaders(token) });
  return res.data;
}

// ── Booster ──
export async function openBooster(token: string, itemId: number) {
  const res = await axios.post(
    `${API}/shop/booster/open`,
    { item_id: itemId },
    { headers: { Authorization: `Bearer ${token}` } }
  );
  return res.data;
}

// ── P2P Market ──
export async function listInventoryItem(token: string, inventoryId: number, quantity: number, priceGal: number) {
  const res = await axios.post(
    `${API}/market/inventory/list`,
    { inventory_id: inventoryId, quantity, price_gal: priceGal },
    { headers: { Authorization: `Bearer ${token}` } }
  );
  return res.data;
}

// ── Equipment ──
export async function equipAccessory(token: string, axolotitoId: number, itemId: number, slot: string) {
  const res = await axios.post(
    `${API}/auth/axolotitos/${axolotitoId}/equip`,
    { item_id: itemId, slot },
    { headers: { Authorization: `Bearer ${token}` } }
  );
  return res.data;
}

export async function unequipAccessory(token: string, axolotitoId: number, slot: string) {
  const res = await axios.post(
    `${API}/auth/axolotitos/${axolotitoId}/unequip`,
    { slot },
    { headers: { Authorization: `Bearer ${token}` } }
  );
  return res.data;
}

// ── Board Management ──
export async function createRandomBoard(token: string, name: string) {
  const res = await axios.post(
    `${API}/board/create/random`,
    { name, card_ids: [] },
    { headers: { Authorization: `Bearer ${token}` } }
  );
  return res.data;
}

export async function unlockNewSlot(token: string) {
  const res = await axios.post(
    `${API}/board/slots/unlock`,
    {},
    { headers: { Authorization: `Bearer ${token}` } }
  );
  return res.data;
}

export async function claimAllStaking(token: string) {
  const res = await axios.post(
    `${API}/board/claim-staking/all`,
    {},
    { headers: { Authorization: `Bearer ${token}` } }
  );
  return res.data;
}

export async function deleteBoard(token: string, boardId: number) {
  const res = await axios.delete(
    `${API}/board/${boardId}`,
    { headers: { Authorization: `Bearer ${token}` } }
  );
  return res.data;
}

export async function claimBoardStaking(token: string, boardId: number) {
  const res = await axios.post(
    `${API}/board/${boardId}/claim-staking`,
    {},
    { headers: { Authorization: `Bearer ${token}` } }
  );
  return res.data;
}

export async function listBoardForRent(token: string, boardId: number, rentFeeGal: number, rentShareOwnerPct: number) {
  const res = await axios.post(
    `${API}/board/${boardId}/list-rent`,
    { rent_fee_gal: rentFeeGal, rent_share_owner_pct: rentShareOwnerPct },
    { headers: { Authorization: `Bearer ${token}` } }
  );
  return res.data;
}

export async function cancelRentalListing(token: string, boardId: number) {
  const res = await axios.post(
    `${API}/board/${boardId}/cancel-rent`,
    {},
    { headers: { Authorization: `Bearer ${token}` } }
  );
  return res.data;
}
